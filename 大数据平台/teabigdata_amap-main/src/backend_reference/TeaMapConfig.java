package com.teadata.config;

import java.io.Serializable;
import java.util.Map;

/**
 * Configuration class for the Tea Tree Big Data Platform Frontend.
 * This class is used to serialize configuration data sent to the Vue.js frontend,
 * allowing dynamic control over UI elements, initial states, and text content.
 */
public class TeaMapConfig implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * The main title displayed at the top of the application.
     * Default: "中国古茶树大数据 | 数据可视化平台"
     */
    private String appTitle;

    /**
     * Initial map viewing mode.
     * Options: "2D", "3D"
     */
    private String initialMapMode;

    /**
     * Initial data visualization mode.
     * Options: "mass" (MassMarks), "cluster" (MarkerCluster)
     */
    private String initialViewMode;

    /**
     * Configuration for the visibility of various UI panels.
     */
    private PanelVisibility panelState;

    /**
     * Configuration for filter default values.
     */
    private FilterConfig defaultFilters;

    // --- Inner Classes ---

    public static class PanelVisibility implements Serializable {
        /**
         * Region Selector (Top-Left)
         */
        private boolean region;

        /**
         * Filter Bar (Top-Center)
         */
        private boolean filter;

        /**
         * Map Tools / Style Switcher (Top-Right)
         */
        private boolean tools;

        /**
         * Lancang River Statistics Panel (Bottom-Left)
         */
        private boolean lancangStats;

        // Getters and Setters
        public boolean isRegion() { return region; }
        public void setRegion(boolean region) { this.region = region; }

        public boolean isFilter() { return filter; }
        public void setFilter(boolean filter) { this.filter = filter; }

        public boolean isTools() { return tools; }
        public void setTools(boolean tools) { this.tools = tools; }

        public boolean isLancangStats() { return lancangStats; }
        public void setLancangStats(boolean lancangStats) { this.lancangStats = lancangStats; }
        
        // Factory method for defaults
        public static PanelVisibility defaults() {
            PanelVisibility pv = new PanelVisibility();
            pv.setRegion(true);
            pv.setFilter(true);
            pv.setTools(true);
            pv.setLancangStats(true); // Default visible
            return pv;
        }
    }

    public static class FilterConfig implements Serializable {
        private String defaultRegionName; // e.g., "云南省"
        private Double minDbh;
        private Double maxDbh;

        // Getters and Setters ...
        public String getDefaultRegionName() { return defaultRegionName; }
        public void setDefaultRegionName(String defaultRegionName) { this.defaultRegionName = defaultRegionName; }
        
        public Double getMinDbh() { return minDbh; }
        public void setMinDbh(Double minDbh) { this.minDbh = minDbh; }

        public Double getMaxDbh() { return maxDbh; }
        public void setMaxDbh(Double maxDbh) { this.maxDbh = maxDbh; }
    }

    // --- Constructors ---

    public TeaMapConfig() {
        this.appTitle = "中国古茶树大数据 | 数据可视化平台";
        this.initialMapMode = "2D";
        this.initialViewMode = "mass";
        this.panelState = PanelVisibility.defaults();
        this.defaultFilters = new FilterConfig();
    }

    // --- Getters and Setters ---

    public String getAppTitle() {
        return appTitle;
    }

    public void setAppTitle(String appTitle) {
        this.appTitle = appTitle;
    }

    public String getInitialMapMode() {
        return initialMapMode;
    }

    public void setInitialMapMode(String initialMapMode) {
        this.initialMapMode = initialMapMode;
    }

    public String getInitialViewMode() {
        return initialViewMode;
    }

    public void setInitialViewMode(String initialViewMode) {
        this.initialViewMode = initialViewMode;
    }

    public PanelVisibility getPanelState() {
        return panelState;
    }

    public void setPanelState(PanelVisibility panelState) {
        this.panelState = panelState;
    }

    public FilterConfig getDefaultFilters() {
        return defaultFilters;
    }

    public void setDefaultFilters(FilterConfig defaultFilters) {
        this.defaultFilters = defaultFilters;
    }
}
