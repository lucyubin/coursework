install.packages("readxl")
install.packages("dplyr")
install.packages("ggplot2")
library(readxl)
library(dplyr)
library(ggplot2)

setwd("C:/Users/YUBIN/OneDrive - Texas State University/2025 Spring/7301 ADV QUANT METHDS/lab 1/")

# Import the data from the xlsx file
data <- read_excel("GEO7301_Lab1_TravisCntyCensusTract_HousingData2018.xlsx")
head(data)

# Test correlation between dependent and independent variables
cor(data$medianRent, data$medianHomeValue)

# Fit the linear regression model
model <- lm(medianRent ~ medianHomeValue, data = data)

# View the model summary
summary(model)

# Scatter plot with regression line
ggplot(data, aes(x = medianHomeValue, y = medianRent)) + 
  geom_point() +  # Scatter plot
  geom_smooth(method = "lm", col = "blue") +  # Regression line (linear model)
  labs(title = "Linear Regression: medianRent vs. medianHomeValue", 
       x = "Median Home Value", 
       y = "Median Rent") +
  theme_minimal()

# Extract sample
sampled_data <- data %>%
  distinct(GEOID, .keep_all = TRUE) %>%  # Keep only unique GEOID rows
  sample_n(size = 30, replace = FALSE)

# Test correlation between dependent and independent variables
cor(sampled_data$medianRent, sampled_data$medianHomeValue)

# Fit the linear regression model
model2 <- lm(medianRent ~ medianHomeValue, data = sampled_data)
summary(model2)

# Scatter plot with regression line
ggplot(sampled_data, aes(x = medianHomeValue, y = medianRent)) + 
  geom_point() +  # Scatter plot
  geom_smooth(method = "lm", col = "blue") +  # Regression line (linear model)
  labs(title = "Linear Regression: medianRent vs. medianHomeValue", 
       x = "Median Home Value", 
       y = "Median Rent") +
  theme_minimal()
