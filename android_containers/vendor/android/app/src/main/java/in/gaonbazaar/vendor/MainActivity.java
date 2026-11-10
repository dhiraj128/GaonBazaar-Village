package in.gaonbazaar.vendor;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.webkit.GeolocationPermissions;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.content.FileProvider;
import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * GaonBazaar Native Android Web Container
 * Bridges native Android hardware APIs (Camera capture="environment", WebRTC Barcode Scanner, GPS)
 * to high-performance PWA WebViews.
 */
public class MainActivity extends AppCompatActivity {{
    private WebView webView;
    private ValueCallback<Uri[]> filePathCallback;
    private Uri cameraImageUri;
    private static final int FILE_CHOOSER_REQUEST_CODE = 1001;
    private static final int PERMISSION_REQUEST_CODE = 1002;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        requestAppPermissions();

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setGeolocationEnabled(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {{
                if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("file://")) {{
                    return false;
                }}
                try {{
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }} catch (Exception e) {{
                    return false;
                }}
            }}
        }});

        webView.setWebChromeClient(new WebChromeClient() {{
            // WebRTC barcode camera stream permission grant
            @Override
            public void onPermissionRequest(final PermissionRequest request) {{
                runOnUiThread(() -> {{
                    request.grant(request.getResources());
                }});
            }}

            // Geolocation permission grant
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {{
                callback.invoke(origin, true, false);
            }}

            // Native Camera capture="environment" file chooser bridge
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {{
                if (MainActivity.this.filePathCallback != null) {{
                    MainActivity.this.filePathCallback.onReceiveValue(null);
                }}
                MainActivity.this.filePathCallback = filePathCallback;

                boolean isCapture = fileChooserParams.isCaptureEnabled();
                String[] acceptTypes = fileChooserParams.getAcceptTypes();
                boolean isImage = false;
                if (acceptTypes != null) {{
                    for (String type : acceptTypes) {{
                        if (type.contains("image")) {{
                            isImage = true;
                            break;
                        }}
                    }}
                }}

                Intent takePictureIntent = null;
                if (isCapture || isImage) {{
                    takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                    if (takePictureIntent.resolveActivity(getPackageManager()) != null) {{
                        File photoFile = null;
                        try {{
                            photoFile = createImageFile();
                        }} catch (IOException ex) {{
                            // Error creating file
                        }}
                        if (photoFile != null) {{
                            cameraImageUri = FileProvider.getUriForFile(
                                MainActivity.this,
                                getPackageName() + ".fileprovider",
                                photoFile
                            );
                            takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, cameraImageUri);
                        }}
                    }}
                }}

                Intent contentSelectionIntent = fileChooserParams.createIntent();

                Intent[] intentArray;
                if (takePictureIntent != null && cameraImageUri != null) {{
                    intentArray = new Intent[]{{takePictureIntent}};
                }} else {{
                    intentArray = new Intent[0];
                }}

                Intent chooserIntent = new Intent(Intent.ACTION_CHOOSER);
                chooserIntent.putExtra(Intent.EXTRA_INTENT, contentSelectionIntent);
                chooserIntent.putExtra(Intent.EXTRA_TITLE, "Select Action or Take Photo");
                chooserIntent.putExtra(Intent.EXTRA_INITIAL_INTENTS, intentArray);

                startActivityForResult(chooserIntent, FILE_CHOOSER_REQUEST_CODE);
                return true;
            }}
        }});

        webView.loadUrl("file:///android_asset/public/index.html");
    }}

    private File createImageFile() throws IOException {{
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(new Date());
        String imageFileName = "JPEG_" + timeStamp + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        return File.createTempFile(imageFileName, ".jpg", storageDir);
    }}

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {{
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {{
            if (filePathCallback == null) return;
            Uri[] results = null;
            if (resultCode == RESULT_OK) {{
                if (data == null || data.getData() == null) {{
                    if (cameraImageUri != null) {{
                        results = new Uri[]{{cameraImageUri}};
                    }}
                }} else {{
                    String dataString = data.getDataString();
                    if (dataString != null) {{
                        results = new Uri[]{{Uri.parse(dataString)}};
                    }}
                }}
            }}
            filePathCallback.onReceiveValue(results);
            filePathCallback = null;
        }} else {{
            super.onActivityResult(requestCode, resultCode, data);
        }}
    }}

    private void requestAppPermissions() {{
        String[] permissions = {{
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.RECORD_AUDIO
        }};
        ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
    }}

    @Override
    public void onBackPressed() {{
        if (webView != null && webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
}}
