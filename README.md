# JobPostingSalaryEstimator
A Job Posting Scraper and Intelligent Salary Estimator, built with XGBoost.

## Scraping
All scraping of job postings and details was done using Python Selenium. Over 500 unique postings were scraped from LinkedIn across several search terms relevant to Computer/Data Science. For each posting, the following attributes were scraped: job title, employer name, location, number of applicants, description, and salary (if available). Since most postings did not include a salary, a GlassDoor Scraper was used to find salary estimates for the remaining postings.

## Data Processing
Simple Pandas string computation was used to process posting attributes into usable numerical features.

## Feature Engineering
Binary features were created for each province, and for the 10 most popular cities. Additionally, title pronouns (senior, lead, director, etc.) and title keywords (scientist, engineer, remote, etc.) were also captured in binary variables. String parsing was applied to the description of each posting to determine the required experience with the most years, and also the number of experiences required. Lastly, the number of applicants was normalized to the range [0, 1] by dividing the column by 100.

## Model Training
The Bayesian Optimization package was used to find the optimal hyperparameters for the model, which used the XGBoost algorithm. The model was trained on 90% of the postings (approximately 540) to predict the annual salary, and tested on the remaining 10% of postings (approximately 60).

## Model Evaluation
The mean absolute error of the final model on the test data was approximately $13600. Furthermore, 85% of the predictions were within $17500 of the true annual salary.

## Model Limitations
1. The model was only trained on job postings from a narrow list of professions and industries, and so is not predictive of industries not represented in the dataset.

2. The model tends to underestimate the highest annual salaries in the dataset. I suspect this is because the highest salaries are typically offered at the largest/best firms, and there are no variables measuring firm size in the training data. You can visualize this limitation in the below graph:
   
![True vs Predicted Distribution](https://github.com/Evan-B-Warner/JobPostingSalaryEstimator/blob/bfd97051f850ebc17b2c459ab6942d759e908f3c/data/prediction_vs_true_distribution.JPG)
