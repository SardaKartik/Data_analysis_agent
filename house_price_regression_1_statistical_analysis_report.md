# Statistical Report for house_price_regression_dataset.csv
**Dataset Shape:** 1000 rows, 8 columns

## Numerical Features Analysis

### Square_Footage
- Mean: 2815.42
- Median: 2862.50
- Std Dev: 1255.51
- Range: 503.00 to 4999.00
- IQR: 2100.00

### Num_Bedrooms
- Mean: 2.99
- Median: 3.00
- Std Dev: 1.43
- Range: 1.00 to 5.00
- IQR: 2.00

### Num_Bathrooms
- Mean: 1.97
- Median: 2.00
- Std Dev: 0.82
- Range: 1.00 to 3.00
- IQR: 2.00

### Year_Built
- Mean: 1986.55
- Median: 1986.00
- Std Dev: 20.63
- Range: 1950.00 to 2022.00
- IQR: 35.25

### Lot_Size
- Mean: 2.78
- Median: 2.81
- Std Dev: 1.30
- Range: 0.51 to 4.99
- IQR: 2.26

### Garage_Size
- Mean: 1.02
- Median: 1.00
- Std Dev: 0.81
- Range: 0.00 to 2.00
- IQR: 2.00

### Neighborhood_Quality
- Mean: 5.62
- Median: 6.00
- Std Dev: 2.89
- Range: 1.00 to 10.00
- IQR: 5.00

### House_Price
- Mean: 618861.02
- Median: 628267.29
- Std Dev: 253568.06
- Range: 111626.85 to 1108236.84
- IQR: 425493.05

## Correlation Analysis

### Correlation Matrix
|                      |   Square_Footage |   Num_Bedrooms |   Num_Bathrooms |   Year_Built |   Lot_Size |   Garage_Size |   Neighborhood_Quality |   House_Price |
|:---------------------|-----------------:|---------------:|----------------:|-------------:|-----------:|--------------:|-----------------------:|--------------:|
| Square_Footage       |             1    |          -0.04 |           -0.03 |        -0.02 |       0.09 |          0.03 |                  -0.01 |          0.99 |
| Num_Bedrooms         |            -0.04 |           1    |            0.02 |        -0.02 |      -0.01 |          0.11 |                  -0.05 |          0.01 |
| Num_Bathrooms        |            -0.03 |           0.02 |            1    |        -0.02 |       0.03 |          0.02 |                   0.02 |         -0    |
| Year_Built           |            -0.02 |          -0.02 |           -0.02 |         1    |      -0.06 |         -0.03 |                  -0.01 |          0.05 |
| Lot_Size             |             0.09 |          -0.01 |            0.03 |        -0.06 |       1    |          0    |                   0.04 |          0.16 |
| Garage_Size          |             0.03 |           0.11 |            0.02 |        -0.03 |       0    |          1    |                  -0.01 |          0.05 |
| Neighborhood_Quality |            -0.01 |          -0.05 |            0.02 |        -0.01 |       0.04 |         -0.01 |                   1    |         -0.01 |
| House_Price          |             0.99 |           0.01 |           -0    |         0.05 |       0.16 |          0.05 |                  -0.01 |          1    |

### Strong Feature Correlations
*Correlations with absolute value > 0.5*
| Feature 1      | Feature 2   |   Correlation | Strength        |
|:---------------|:------------|--------------:|:----------------|
| Square_Footage | House_Price |          0.99 | Strong Positive |

**Observations:**

*   **Strong Correlation:** There's a very strong positive correlation (0.99) between `Square_Footage` and `House_Price`. This indicates that as the square footage of a house increases, its price tends to increase significantly. This is a key factor to consider in any predictive model for house prices.
*   **Weak Correlations:** Other features like `Num_Bedrooms`, `Num_Bathrooms`, `Year_Built`, `Lot_Size`, `Garage_Size`, and `Neighborhood_Quality` have weak correlations with `House_Price`. While they might still contribute to the price, their individual impact appears to be much less than that of square footage.
*   **Data Distribution:** The means and medians for most features are relatively close, suggesting approximately symmetrical distributions. However, `Square_Footage` and `House_Price` have substantial standard deviations, indicating a wide range of values and potential variability in the data.
*   **Potential Outliers:** The ranges for `Square_Footage` and `House_Price` are quite large, suggesting the presence of potential outliers. Further investigation might be needed to determine if these outliers are genuine or data errors.

**Recommendations for Further Analysis:**

1.  **Regression Modeling:** Build a linear regression model with `House_Price` as the target variable and `Square_Footage` as the primary predictor. Explore adding other features to see if they improve the model's performance.
2.  **Outlier Analysis:** Investigate the potential outliers in `Square_Footage` and `House_Price`. Determine if they are valid data points or errors that need to be corrected or removed.
3.  **Non-linear Relationships:** Explore potential non-linear relationships between the features and `House_Price`. For example, the relationship between `Lot_Size` and `House_Price` might not be linear.
4.  **Feature Interactions:** Examine potential interaction effects between features. For example, the effect of `Square_Footage` on `House_Price` might depend on the `Neighborhood_Quality`.
5.  **Residual Analysis:** After building a regression model, perform residual analysis to check for any patterns or heteroscedasticity in the residuals. This can help identify areas where the model can be improved.
6. **Polynomial Regression:** Consider polynomial regression with Square_Footage to see if a curve better fits the data and improves prediction accuracy.