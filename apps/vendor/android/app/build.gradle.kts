import java.util.Properties
import java.io.FileInputStream

val keystoreProperties = Properties()
val keystorePropertiesFile = rootProject.file("key.properties")
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.gaonbazaar.vendor.vendor"
    compileSdk = 36

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    signingConfigs {
        create("release") {
            val keyPasswordProp = keystoreProperties.getProperty("keyPassword")
            val keyAliasProp = keystoreProperties.getProperty("keyAlias")
            val storeFilePath = keystoreProperties.getProperty("storeFile")
            val storePasswordProp = keystoreProperties.getProperty("storePassword")

            if (keyPasswordProp != null && keyAliasProp != null && storeFilePath != null && storePasswordProp != null) {
                val resolvedStoreFile = rootProject.file(storeFilePath)
                if (resolvedStoreFile.exists()) {
                    keyAlias = keyAliasProp
                    keyPassword = keyPasswordProp
                    storeFile = resolvedStoreFile
                    storePassword = storePasswordProp
                } else {
                    throw GradleException("Release keystore file not found at: ${resolvedStoreFile.absolutePath}")
                }
            } else {
                throw GradleException("Release signing properties missing in key.properties (storeFile, storePassword, keyAlias, keyPassword required). Debug signing fallback is strictly disabled.")
            }
        }
    }

    defaultConfig {
        applicationId = "com.gaonbazaar.vendor"
        minSdk = 24
        targetSdk = 36
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
