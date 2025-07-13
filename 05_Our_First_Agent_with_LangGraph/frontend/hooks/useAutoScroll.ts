import { useRef, useEffect, useCallback } from 'react';

interface UseAutoScrollOptions {
  enabled?: boolean;
  behavior?: ScrollBehavior;
  threshold?: number;
  debounceMs?: number;
}

export const useAutoScroll = (options: UseAutoScrollOptions = {}) => {
  const {
    enabled = true,
    behavior = 'smooth',
    threshold = 100,
    debounceMs = 50,
  } = options;

  const containerRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldAutoScrollRef = useRef(true);
  const lastScrollTopRef = useRef(0);

  // Check if user has scrolled up and disable auto-scroll
  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < threshold;
    
    // If user scrolled up significantly, disable auto-scroll
    if (scrollTop < lastScrollTopRef.current - 50) {
      shouldAutoScrollRef.current = false;
    }
    
    // If user scrolled back near bottom, re-enable auto-scroll
    if (isNearBottom) {
      shouldAutoScrollRef.current = true;
    }
    
    lastScrollTopRef.current = scrollTop;
  }, [threshold]);

  // Smooth scroll to bottom
  const scrollToBottom = useCallback((force = false) => {
    if (!containerRef.current || (!enabled && !force)) return;
    
    if (!shouldAutoScrollRef.current && !force) return;

    // Clear any pending scroll timeout
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }

    // Debounce scroll to avoid too many scroll events
    scrollTimeoutRef.current = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.scrollTo({
          top: containerRef.current.scrollHeight,
          behavior,
        });
      }
    }, debounceMs);
  }, [enabled, behavior, debounceMs]);

  // Immediately scroll to bottom without animation
  const scrollToBottomInstant = useCallback(() => {
    if (!containerRef.current) return;
    
    containerRef.current.scrollTop = containerRef.current.scrollHeight;
    shouldAutoScrollRef.current = true;
  }, []);

  // Check if element is at bottom
  const isAtBottom = useCallback(() => {
    if (!containerRef.current) return true;
    
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    return scrollHeight - scrollTop - clientHeight < threshold;
  }, [threshold]);

  // Enable auto-scroll (useful for re-enabling after user interaction)
  const enableAutoScroll = useCallback(() => {
    shouldAutoScrollRef.current = true;
    scrollToBottom();
  }, [scrollToBottom]);

  // Disable auto-scroll
  const disableAutoScroll = useCallback(() => {
    shouldAutoScrollRef.current = false;
  }, []);

  // Scroll to specific element
  const scrollToElement = useCallback((element: HTMLElement) => {
    if (!containerRef.current) return;
    
    element.scrollIntoView({
      behavior,
      block: 'nearest',
      inline: 'nearest',
    });
  }, [behavior]);

  // Effect to handle scroll events
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('scroll', handleScroll, { passive: true });
    
    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, [handleScroll]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  // Auto-scroll when new content appears (using MutationObserver)
  useEffect(() => {
    if (!enabled || !containerRef.current) return;

    const container = containerRef.current;
    
    const observer = new MutationObserver(() => {
      scrollToBottom();
    });

    observer.observe(container, {
      childList: true,
      subtree: true,
      characterData: true,
    });

    return () => {
      observer.disconnect();
    };
  }, [enabled, scrollToBottom]);

  // Auto-scroll when window is resized
  useEffect(() => {
    const handleResize = () => {
      if (shouldAutoScrollRef.current) {
        scrollToBottom();
      }
    };

    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [scrollToBottom]);

  return {
    containerRef,
    scrollToBottom,
    scrollToBottomInstant,
    scrollToElement,
    enableAutoScroll,
    disableAutoScroll,
    isAtBottom,
    isAutoScrollEnabled: shouldAutoScrollRef.current,
  };
}; 