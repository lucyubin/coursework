install.packages("sf")
install.packages("spdep")
# Load necessary libraries
library(sf)          # For spatial data handling
library(spdep)       # For spatial analysis
library(ggplot2)     # For plotting
library(tmap)        # For spatial visualization

# set working directory
setwd("*/lab 3")

# read shapefile
shapefile <- st_read("County Map - StratMap_County_poly_20250220/geo_export_36d59802-da3c-496d-a441-92070bc7f00d.shp")
shapefile <- shapefile[, c("name", "geometry")] # select only two columns
  
# read CSV file
df <- read.csv("GEO7301_Labs3to5_CountyVariablesColonLateStage2005to2014.csv")

# join shapefile and CSV file
shapefile <- merge(shapefile, df, by.x = "name", by.y = "NAME", all.x = TRUE)

# select 10 counties
counties <- shapefile[shapefile$name %in% c("Llano", "Travis", "Blanco", 
                                            "Kendall", "Caldwell", "Comal", 
                                            "Gillespie", "Hays", "Guadalupe", 
                                            "Burnet"), ]

# Create a neighbor list using Queen's contiguity
nb <- poly2nb(counties)

# Convert to a spatial weights matrix
w <- nb2listw(nb, style = "W", zero.policy = TRUE)

# Compute spatial lag of AgeAdjstRatio
counties$spatial_lag <- lag.listw(w, counties$AgeAdjstRatio)

# Plot spatial lag scatter plot
ggplot(counties, aes(x = AgeAdjstRatio, y = spatial_lag)) +
  geom_point(color = "blue") +
  geom_smooth(method = "lm", color = "red", se = FALSE) +
  labs(title = "Spatial Lag Plot for Age Adjusted Ratio",
       x = "Age Adjusted Ratio",
       y = "Spatial Lag of Age Adjusted Ratio") +
  theme_minimal()

# Display the spatial weight matrix
print(as.matrix(listw2mat(w)))

'''
         [,1]      [,2]      [,3]      [,4]      [,5]      [,6]      [,7]      [,8]      [,9]     [,10]
16  0.0000000 0.1428571 0.0000000 0.1428571 0.1428571 0.0000000 0.1428571 0.1428571 0.1428571 0.1428571
27  0.3333333 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000 0.3333333 0.3333333
28  0.0000000 0.0000000 0.0000000 0.0000000 0.0000000 0.3333333 0.3333333 0.0000000 0.0000000 0.3333333
46  0.2500000 0.0000000 0.0000000 0.0000000 0.0000000 0.2500000 0.2500000 0.2500000 0.0000000 0.0000000
86  0.3333333 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000 0.3333333 0.3333333 0.0000000
94  0.0000000 0.0000000 0.3333333 0.3333333 0.0000000 0.0000000 0.3333333 0.0000000 0.0000000 0.0000000
105 0.2000000 0.0000000 0.2000000 0.2000000 0.0000000 0.2000000 0.0000000 0.0000000 0.0000000 0.2000000
130 0.3333333 0.0000000 0.0000000 0.3333333 0.3333333 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000
150 0.3333333 0.3333333 0.0000000 0.0000000 0.3333333 0.0000000 0.0000000 0.0000000 0.0000000 0.0000000
227 0.2500000 0.2500000 0.2500000 0.0000000 0.0000000 0.0000000 0.2500000 0.0000000 0.0000000 0.0000000
'''

# Compute Moran's I
moran_test <- moran.test(counties$AgeAdjstRatio, w, zero.policy = TRUE)

# Display Moran's I results
print(moran_test)

'''
	Moran I test under randomisation

data:  counties$AgeAdjstRatio  
weights: w    

Moran I statistic standard deviate = 2.8985, p-value = 0.001875
alternative hypothesis: greater
sample estimates:
Moran I statistic       Expectation          Variance 
       0.41263427       -0.11111111        0.03264982 
'''
