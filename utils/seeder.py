import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Function to generate synthetic customer data
def generate_customer_data(n_customers=1000):
    # Customer IDs
    customer_ids = range(1, n_customers + 1)

    # Gender
    gender = np.random.choice(['Male', 'Female'], size=n_customers)

    # Age
    age = np.random.normal(42, 15, n_customers).astype(int)
    age = np.clip(age, 18, 85)

    # Tenure (months)
    tenure = np.random.exponential(30, n_customers).astype(int)
    tenure = np.clip(tenure, 0, 72)

    # Contract Type
    contract_type = np.random.choice(
        ['Month-to-Month', 'One Year', 'Two Year'],
        size=n_customers,
        p=[0.5, 0.3, 0.2]
    )

    # Monthly Charges
    monthly_charges = np.random.normal(70, 30, n_customers)
    monthly_charges = np.clip(monthly_charges, 20, 150).round(2)

    # Total Charges
    total_charges = (monthly_charges * tenure) * (np.random.normal(0.98, 0.02, n_customers))
    total_charges = np.clip(total_charges, 0, None).round(2)

    # Services
    internet_service = np.random.choice(['DSL', 'Fiber Optic', 'No'], size=n_customers, p=[0.4, 0.4, 0.2])
    phone_service = np.random.choice(['Yes', 'No'], size=n_customers, p=[0.9, 0.1])
    streaming_tv = np.random.choice(['Yes', 'No'], size=n_customers, p=[0.7, 0.3])
    streaming_movies = np.random.choice(['Yes', 'No'], size=n_customers, p=[0.7, 0.3])

    # Payment Method
    payment_method = np.random.choice(
        ['Electronic Check', 'Mailed Check', 'Bank Transfer', 'Credit Card'],
        size=n_customers
    )

    # Satisfaction Score
    satisfaction_score = np.random.normal(3.5, 1, n_customers)
    satisfaction_score = np.clip(satisfaction_score, 1, 5).round(1)

    # Calculate probability of churn based on various factors
    churn_prob = (
        (contract_type == 'Month-to-Month') * 0.2 +
        (monthly_charges > 100) * 0.1 +
        (satisfaction_score < 3) * 0.3 +
        (internet_service == 'Fiber Optic') * 0.1 +
        (payment_method == 'Electronic Check') * 0.1
    )

    # Normalize probabilities
    churn_prob = (churn_prob - churn_prob.min()) / (churn_prob.max() - churn_prob.min())
    churn_prob = churn_prob * 0.5  # Scale down to reasonable churn rate

    # Generate churn based on probability
    churn = np.random.binomial(1, churn_prob)

    # Create DataFrame
    df = pd.DataFrame({
        'CustomerID': customer_ids,
        'Gender': gender,
        'Age': age,
        'Tenure': tenure,
        'ContractType': contract_type,
        'MonthlyCharges': monthly_charges,
        'TotalCharges': total_charges,
        'InternetService': internet_service,
        'PhoneService': phone_service,
        'StreamingTV': streaming_tv,
        'StreamingMovies': streaming_movies,
        'PaymentMethod': payment_method,
        'SatisfactionScore': satisfaction_score,
        'Churn': churn
    })

    return df

# Generate the dataset
df = generate_customer_data(1000)

# Save to CSV
df.to_csv('customer_churn.csv', index=False)

# Display first few rows and basic information
print("Dataset Preview:")
print(df.head())
print("\nDataset Info:")
print(df.info())
print("\nChurn Distribution:")
print(df['Churn'].value_counts(normalize=True))
