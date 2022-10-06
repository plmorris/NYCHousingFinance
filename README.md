# Real Estate Costs in New York City

## Authors
Erick Sanmartin, Peter Morris, Anthony Rondos, Nate Williamson

## Table of Contents
- [Introduction](#Introduction)
- [Requirements](#Requirements)
- [Data Processing & ETL](#Data-Processing-&-ETL)
- [Visualizations](#Visualizations)
- [Results](#Results)
- [Resources](#Resources)

## Introduction
The New York City real estate market is one of the most lucrative and competitive markets in the world. This project seeks to uncover and understand NYC real estate pricing trends, both renting and owning, and use those findings to create a machine learning model that predicts housing prices. Entering a post-COVID19 era, NYC real estate has experienced the highest rent increases in nearly a decade marked by bidding wars due to scarce supply and by ongoing inflation (Zaveri, 2022). Tenants have faced existential questions about whether to renew their leases asking for 30 to 60% more year over year or relocate somewhere in a city where affordable housing is virtually nonexistent (White Karp, 2022). By analyzing the housing market, we will illuminate the current and future geography of this financial services sector. This work will set the stage for a discussion on the distribution of wealth in the city as well as laws and policies regarding the cost of renting and ownership for lending and borrowing stakeholders.

Questions addressed in this report:

1. How has the median cost of purchasing a home varied monthly in the last year?
2. Which neighborhoods’ median rent increased the most for each borough in the last 12 years?
3. What are the most and least expensive neighborhoods for renting?
4. How long until renting costs outweighs owning costs?
5. How do sales in the past 12 months compare with one another by both zip code and borough?
6. How does employee pay compare to sales price in different zip codes of New York City?
7. How do median rent prices for each borough during the pandemic compare to the present?
8. Do property details have a relationship to changing prices in specific neighborhoods?
9. How has public policy influenced real estate prices?
10. Can we predict property prices based on property features and location?

## Requirements
* [conda environment file](https://github.com/nateswill/NYCHousingFinance/blob/master/Code/Dashboard/dash-capstone-env.yml)
* Required python libraries for dashboard and machine learning model
    - pandas
    - numpy
    - matplotlib
    - seaborn
    - plotly
    - dash
    - pymssql
    - ipykernel
    - nbformat>=4.2.0
    - scikit-learn
    - dash-bootstrap-components


## Data Processing & ETL
We used a total of nine datasets in this capstone project with either information about housing costs or economic information by region. We extracted five datasets from the New York City Department of Finance’s open data. These datasets were in the form of comma-separated value text files held rolling property sales information in New York City in the past year, with each dataset pertaining to a different borough. By creating a dataframe for each borough via url, we concatenated all five boroughs into one large New York City Rolling Property Sales dataset. We called two datasets from StreetEasy, a website that provides property sale and rental information for New York City, via API. These two datasets respectively contained property sales information and rental information by neighborhood. We took the final two datasets from the U.S Census website via API to provide economic background and context to the other real estate information extracted. We loaded the NYC Rolling Property Sales into a databrick and used Kafka to automatically stream the data into a consumer and producer. We created another static databrick for the StreetEasy and Census data, and then inputted both databricks into the same normalized SQL database. One can visualize the process as follows:

### Data Pipeline
![data-pipeline]()

### ERD
![erd]()
## Visualizations

![price-events]()
![top3-bot3]()
![rent-breakdown]()
![rent-buy]()
![machine-learn]()

## Results
[Project Report](https://github.com/nateswill/NYCHousingFinance/blob/master/ProjectSpecifications/ProjectTechnicalReport.pdf)

## Sources
[New York City Department of Finance. (2022). Rolling Sales Data. ](https://www1.nyc.gov/site/finance/taxes/property-rolling-sales-data.page)
[Street Easy. (2010-2022).  Sales in NYC, All Home Type, Median Sale Price.](https://streeteasy.com/blog/data-dashboard/?agg=Median&metric=Recorded%20Price&type=Sales)
[Street Easy. (2010-2022).  Rentals in NYC, All Bedroom Count, Median Asking Price.](https://streeteasy.com/blog/data-dashboard/?agg=Median&metric=Asking%20Rent&type=Rentals)
[United States Census Bureau. (2017). Economy-Wide Key Statistics 2017.](https://www.census.gov/data/developers/data-sets/economic-census/2017.html)
[United States Census Bureau. (2020). County Business Patterns: 2020.](https://www.census.gov/data/datasets/2020/econ/cbp/2020-cbp.html)
[United States Census Bureau. (2020). ZIP Code Tabulation Areas.](https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2020&layergroup=ZIP+Code+Tabulation+Areas)
[White Karp, Jennifer. “Hit with 30 Percent (or Higher) Rent Increases, Many NYC Tenants Are in ‘Shock.’” Brick Underground, 2 Mar. 2022.](https://www.brickunderground.com/rent/why-are-landlords-raising-rents-extreme-increase-lease-renewal-nyc)
[Zaveri, Mihir. “Why It’s So Hard to Find an Affordable Apartment in New York.” The New York Times, 1 Aug. 2022.](https://www.nytimes.com/2022/08/01/nyregion/nyc-affordable-apartment-rent.html)
