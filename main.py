from modules.data_collection import ask_questions
from modules.metrics import calculate_metrics
from modules.report import generate_report
from utils.file_io import save_data
from modules.trend_tracking import load_history, plot_progress, weekly_summary

# =========================================
# MAIN PROGRAM
# =========================================
def main():
    print("\n=== Welcome to the Advanced Personal Health Tracker ===\n")
    print("Please answer the following questions accurately to generate your health report.\n")

    # 1. Collect user input
    user_data = ask_questions()

    # 2. Calculate metrics
    metrics = calculate_metrics(user_data)
    
    # 3. Generate detailed report + interactive dashboard
    generate_report(user_data, metrics)

    # 4. Save data with timestamp and check alerts
    save_data(user_data, metrics)

    print("\n📈 Generating trend visualizations...\n")
    df = load_history(filename="health_history.json")
    plot_progress(df)

    print("\n🗓️ Weekly Summary Report:\n")
    weekly_summary(df)

    print("\nThank you for using the Advanced Health Tracker! 🏥\n")
    print("You can re-run the program daily to track progress and receive alerts for changes in your health metrics.\n")

# =========================================
# Entry Point
# =========================================
if __name__ == "__main__":
    main()
