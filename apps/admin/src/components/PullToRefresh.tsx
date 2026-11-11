import React, { useState, useRef, useEffect } from 'react';
import { RefreshCw, ArrowDown } from 'lucide-react';

interface PullToRefreshProps {
  children: React.ReactNode;
  onRefresh?: () => void;
  threshold?: number;
  className?: string;
}

export function PullToRefresh({
  children,
  onRefresh,
  threshold = 70,
  className = '',
}: PullToRefreshProps) {
  const [pullDistance, setPullDistance] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const startYRef = useRef(0);
  const isDraggingRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    if (isRefreshing) return;
    // Only allow pull-down if window or container is scrolled to the absolute top
    const isAtTop = (window.scrollY || document.documentElement.scrollTop || 0) <= 0;
    if (isAtTop) {
      startYRef.current = e.touches[0].clientY;
      isDraggingRef.current = true;
    }
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (!isDraggingRef.current || isRefreshing) return;
    const currentY = e.touches[0].clientY;
    const diff = currentY - startYRef.current;

    if (diff > 0) {
      // Apply rubber-band resistance damping factor
      const distance = Math.min(diff * 0.45, 110);
      setPullDistance(distance);
    } else {
      setPullDistance(0);
      isDraggingRef.current = false;
    }
  };

  const handleTouchEnd = () => {
    if (!isDraggingRef.current || isRefreshing) return;
    isDraggingRef.current = false;

    if (pullDistance >= threshold) {
      setIsRefreshing(true);
      setPullDistance(threshold * 0.7); // Snap to spinner height

      // Execute pull-to-refresh logic: trigger reload
      setTimeout(() => {
        if (onRefresh) {
          onRefresh();
        } else {
          window.location.reload();
        }
      }, 400);
    } else {
      setPullDistance(0);
    }
  };

  const isTriggered = pullDistance >= threshold;

  return (
    <div
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      className={`relative min-h-screen ${className}`}
    >
      {/* Pull-to-Refresh Visual Indicator Drawer */}
      <div
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center pointer-events-none transition-transform duration-150 ease-out"
        style={{
          transform: `translateY(${Math.max(0, pullDistance - 45)}px)`,
          opacity: pullDistance > 10 || isRefreshing ? 1 : 0,
        }}
      >
        <div className="bg-white/95 backdrop-blur-md px-4 py-2 rounded-full shadow-lg border border-slate-200 flex items-center space-x-2 text-xs font-semibold text-slate-700">
          {isRefreshing ? (
            <>
              <RefreshCw className="w-4 h-4 text-[#0F9D58] animate-spin" />
              <span>रीफ़्रेश हो रहा है... / Refreshing...</span>
            </>
          ) : isTriggered ? (
            <>
              <RefreshCw className="w-4 h-4 text-[#0F9D58] animate-spin" />
              <span className="text-[#0F9D58]">छोड़कर रीफ़्रेश करें / Release to refresh</span>
            </>
          ) : (
            <>
              <ArrowDown className="w-4 h-4 text-slate-500 animate-bounce" />
              <span>नीचे खींचें / Pull down to refresh</span>
            </>
          )}
        </div>
      </div>

      {/* Main Content with subtle push-down transform while pulling */}
      <div
        style={{
          transform: pullDistance > 0 ? `translateY(${pullDistance * 0.5}px)` : 'none',
          transition: isDraggingRef.current ? 'none' : 'transform 200ms ease-out',
        }}
      >
        {children}
      </div>
    </div>
  );
}

export default PullToRefresh;
