package com.teamap.model;

/**
 * Model representing a Tea Tree entity, corresponding to frontend JSON data.
 */
public class Tea {
    private String name;
    private double lng;
    private double lat;
    private double dbh;
    private String province;
    private String city;
    private String district;
    private String township;
    private String riverBasin;
    private String mountainRange;

    // Getters and Setters

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public double getLng() { return lng; }
    public void setLng(double lng) { this.lng = lng; }

    public double getLat() { return lat; }
    public void setLat(double lat) { this.lat = lat; }

    public double getDbh() { return dbh; }
    public void setDbh(double dbh) { this.dbh = dbh; }

    public String getProvince() { return province; }
    public void setProvince(String province) { this.province = province; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getDistrict() { return district; }
    public void setDistrict(String district) { this.district = district; }

    public String getTownship() { return township; }
    public void setTownship(String township) { this.township = township; }

    public String getRiverBasin() { return riverBasin; }
    public void setRiverBasin(String riverBasin) { this.riverBasin = riverBasin; }

    public String getMountainRange() { return mountainRange; }
    public void setMountainRange(String mountainRange) { this.mountainRange = mountainRange; }
}
