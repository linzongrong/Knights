package com.teamap.config;

import org.springframework.context.annotation.Configuration;

/**
 * Backend configuration for UI settings, including Internationalization support.
 */
@Configuration
public class TeaMapUIConfig {

    private String language; // 'zh' or 'en'
    private boolean showWatermark;
    private String defaultMapStyle;

    public TeaMapUIConfig() {
        this.language = "zh";
        this.showWatermark = false;
        this.defaultMapStyle = "amap://styles/grey";
    }

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }

    public boolean isShowWatermark() {
        return showWatermark;
    }

    public void setShowWatermark(boolean showWatermark) {
        this.showWatermark = showWatermark;
    }

    public String getDefaultMapStyle() {
        return defaultMapStyle;
    }

    public void setDefaultMapStyle(String defaultMapStyle) {
        this.defaultMapStyle = defaultMapStyle;
    }
}
