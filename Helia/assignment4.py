from datetime import date as dt_date, datetime
from abc import ABC, abstractmethod
import csv


def process_until_date(until_date):
    """
    Converts until_date to a datetime.date object.
    Accepts:
      - None -> returns today's date
      - datetime.date -> returns as is
      - string in 'YYYY-MM-DD' -> returns datetime.date
    Raises ValueError if string is not a valid date.
    """
    if until_date is None:
        return dt_date.today()  # default to today
    elif isinstance(until_date, dt_date):
        return until_date
    elif isinstance(until_date, str):
        return datetime.strptime(until_date, "%Y-%m-%d").date()
    else:
        raise ValueError("until_date must be None, a date, or a string in YYYY-MM-DD format")


class Budget(ABC):
    """Abstract base class for budget tracking."""

    def __init__(self):
        # Each expense is a dict: {"date": "YYYY-MM-DD", "category": str, "location": str, "cost": float}
        self.expenses = []

    def add_expense(self, category, location, cost, expense_date=None):
        """
        Add an expense record.
        :param category: expense category (str)
        :param location: where the money was spent (str)
        :param cost: cost of expense (float)
        :param expense_date: ISO format string YYYY-MM-DD or None (defaults to today)
        """
        expense_date = process_until_date(expense_date)
        self.expenses.append({
            "date": expense_date,
            "category": category,
            "location": location,
            "cost": cost
        })

    def total_expenses(self, until_date=None):
        """
        Calculate total expenses up to and including a given date.
        :param until_date: date (datetime.date or "YYYY-MM-DD"), defaults to today
        :return: total expense (float)
        """
        until_date = process_until_date(until_date)

        return sum(
            e["cost"]
            for e in self.expenses
            if e["date"] <= until_date
        )

    def total_by_category(self, until_date=None):
        """
        Calculate total expenses per category up to and including a given date.
        :param until_date: date (datetime.date or "YYYY-MM-DD"), defaults to today
        :return: dict {category: total_spent}
        """
        until_date = process_until_date(until_date)
        totals = {}
        for e in self.expenses:
            expense_date = e["date"]
            if expense_date <= until_date:
                totals[e["category"]] = totals.get(e["category"], 0) + e["cost"]
        return totals

    @abstractmethod
    def summary(self, date):
        """Abstract method: subclasses must implement their own summary printing."""
        pass

    @abstractmethod
    def export_csv(self, filename, until_date=None):
        """Abstract method: subclasses must implement their own CSV export."""
        pass


# --------------------------------------------------Start Editing Here-----------------------------------------------------
class MonthlyBudget(Budget):
    """Manage a monthly budget with category goals and expenses."""

    def __init__(self, month, year, parent=None):
        super().__init__()
        self.month = month
        self.year = year
        self.goals = {}  # category -> goal amount
        self.parent = parent

    def set_goal(self, category, amount):
        """Set or update a monthly goal for a category."""
        self.goals[category] = amount


    def add_expense(self, category, location, cost, expense_date=None):
        """
        Add an expense to this month.
        Default date is today.
        """
        expense_date = process_until_date(expense_date)
        super().add_expense(category, location, cost, expense_date)
        # report to yearly parent if exists
        if self.parent:
            self.parent.add_expense(category, location, cost, expense_date)

    def spend_by_category(self, until_date=None):
        """Return total spending per category for this month up to a given date.
        by default, that date is today"""
        until_date = process_until_date(until_date)
        totals = {}
        for expense in self.expenses:
            if expense["date"] <= until_date: #Checking if the date of the expense is before the current date
                if expense["category"] not in totals:
                    totals[expense["category"]] = expense["cost"] #add category if it doesnt exist
                else :
                    totals[expense["category"]] += expense["cost"] # Sum the values if the category already exists
        return totals


    def remaining_in_category(self, category, until_date=None):
        """Return remaining money in a category until a given date."""
        until_date = process_until_date(until_date)
        spend = self.spend_by_category(until_date) #Calling function before to get the totals
        return self.goals[category] - spend[category] #subtracting the goal by this total

    def summary(self, until_date=None):
        self.month_summary()

    def month_summary(self, until_date=None):
        """Print a summary table of goals, spent, remaining, and status."""
        until_date = process_until_date(until_date)
        totals = self.spend_by_category(until_date)
        categories = set(self.goals.keys()) | set(totals.keys())

        print(f"\n📅 Monthly Budget Summary for {self.month}/{self.year}")
        print("-" * 65)
        print(f"{'Category':<15}{'Goal':<10}{'Spent':<10}{'Remaining':<12}{'Status'}")
        print("-" * 65)

        for cat in categories:
            goal = self.goals.get(cat, 0)
            spent = totals.get(cat, 0)
            remaining = goal - spent
            status = "Within Budget" if remaining >= 0 else "Overspent"
            print(f"{cat:<15}${goal:<9.2f}${spent:<9.2f}${max(remaining, 0):<11.2f}{status}")
        # List overspent categories
        overspent = [cat for cat, spent in totals.items() if spent > self.goals.get(cat, 0)]
        if overspent:
            print("\n⚠️ Overspent categories:", ", ".join(overspent))
        print("-" * 65)

    def daily_summary(self, day):
        """Show detailed expenses for a given day (category, location, cost)."""
        day = process_until_date(day)
        print(f"\n📆 Daily Summary for {day.isoformat()}")
        print("-" * 50)
        print(f"{'Category':<15}{'Location':<20}{'Cost'}")
        print("-" * 50)
        for e in self.expenses:
            expense_date = e["date"]
            if expense_date == day:
                print(f"{e['category']:<15}{e['location']:<20}${e['cost']:.2f}")
        print("-" * 50)

    def export_csv(self, filename, until_date=None):
        """Export a CSV report with categories, goals, spent, remaining, and status."""
        until_date = process_until_date(until_date)
        totals = self.spend_by_category(until_date)

        categories = set(self.goals.keys()) | set(totals.keys())

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Goal", "Spent", "Remaining", "Status"])
            for cat in categories:
                goal = self.goals.get(cat, 0)
                spent = totals.get(cat, 0)
                remaining = goal - spent
                status = "Within Budget" if remaining >= 0 else "Overspent"
                writer.writerow([cat, goal, spent, max(remaining, 0), status])


class YearlyBudget(Budget):
    """Manage a yearly budget with incomes, expenses, and savings goal."""

    def __init__(self, year):
        super().__init__()
        self.year = year
        self.incomes = []  # list of dicts: {"amount": float, "source": str}
        self.savings_goal = 0

    def add_income(self, amount, source=""):
        """Add an income record with optional source."""
        self.incomes.append((amount, source))


    def set_savings_goal(self, amount):
        """Set the yearly savings goal."""
        self.savings_goal = amount #assigns

    def total_income(self):
        """Return total income so far."""
        total_income = 0 #creates variable with initial value 0
        for income in self.incomes:  #goes through the income list and adds the amount to the variable we created
            total_income += income[0]
        return total_income

    def total_expenses(self, until_date=None):
        """Return total expenses for the year up to a given date."""
        until_date = process_until_date(until_date)
        return super().total_expenses(until_date)

    def actual_savings(self, until_date=None):
        """Calculate actual savings = total income - total expenses (up to a date)."""
        until_date = process_until_date(until_date)
        actual_savings = self.total_income() - self.total_expenses(until_date)
        return actual_savings

    def goal_status(self, until_date=None):
        """Return a string indicating whether the savings goal is met."""
        until_date = process_until_date(until_date)
        if self.savings_goal <= self.actual_savings(until_date):
            return "Y"
        else:
            return "N"


    def summary(self, until_date=None):
        """Print yearly budget summary, including total income, expenses, savings, and status."""
        until_date = process_until_date(until_date)
        totals = {}
        for e in self.expenses:
            expense_date = e["date"]
            if expense_date.year == self.year and (until_date is None or expense_date <= until_date):
                totals[e["category"]] = totals.get(e["category"], 0) + e["cost"]

        print(f"\n📅 Yearly Budget Summary for {self.year}")
        print("-" * 50)
        print(f"{'Category':<20}{'Total Spent'}")
        print("-" * 50)
        for cat, total in totals.items():
            print(f"{cat:<20}${total:.2f}")
        print("-" * 50)
        print(f"{'Total Income':<20}${self.total_income():.2f}")
        print(f"{'Total Expenses':<20}${self.total_expenses(until_date):.2f}")
        print(f"{'Actual Savings':<20}${self.actual_savings(until_date):.2f}")
        print(f"{'Savings Goal':<20}${self.savings_goal:.2f}")
        print("Status: Goal" + " met" if self.goal_status(until_date) == "Y" else " not met")
        print("-" * 50)

    def export_csv(self, filename, until_date=None):
        """Export a yearly budget summary as a CSV file."""
        # total category
        # totals,
        # income, total
        # expenses, actual
        # savings, saving
        # goal, and goal
        # status.
        totals = {}
        for e in self.expenses:
            expense_date = e["date"]
            if expense_date.year == self.year and (until_date is None or expense_date <= until_date):
                totals[e["category"]] = totals.get(e["category"], 0) + e["cost"]

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["category", "Total category", "Total income", "Total expenses", "Total savings", "Goal", "Status"])
            for cat, total in totals.items():
                writer.writerow([cat, total, self.total_income(), self.total_expenses(), self.actual_savings(), self.savings_goal, self.goal_status()])

        # TODO 11, please refer to the expoert_csv in MonthlyBudget, they are very similar.

# --------------------------------------------------------------Test Your Code!-------------------------------------------------------------------------
if __name__ == "__main__":
    # Create yearly budget for 2025
    year_budget = YearlyBudget(year=2025)

    # -----------------------------------MonthlyBudget------------------------------------------
    # Create a monthly budget for September 2025
    sept_budget = MonthlyBudget(month=9, year=2025, parent=year_budget)
    aug_budget = MonthlyBudget(month=8, year=2025, parent=year_budget)
    # Set category goals
    sept_budget.set_goal("Groceries", 500)
    sept_budget.set_goal("Eating Out", 200)
    sept_budget.set_goal("Travel", 300)
    sept_budget.set_goal("Groceries", 800)

    # Add expenses
    sept_budget.add_expense("Groceries", "AH", 120, "2025-09-01")
    sept_budget.add_expense("Eating Out", "McDonalds", 15, "2025-09-01")
    sept_budget.add_expense("Groceries", "Jumbos", 80, "2025-09-05")
    sept_budget.add_expense("Travel", "NS", 50, "2025-09-07")
    sept_budget.add_expense("Relax", "Pathé", 50, "2025-09-10")
    sept_budget.add_expense("Eating Out", "Sushi Bar", 10)  # default today

    aug_budget.add_expense("Groceries", "AH", 120, "2025-08-01")
    aug_budget.add_expense("Eating Out", "Taxes Roadhouse", 85, "2025-08-12")

    # Print monthly summary (this function calls spend_by_category)
    sept_budget.month_summary() #groceries 200 eating out 25 travel 50 relax 50
                                #groceries goal 800
                                #eating out goal 200
                                #travel goal 300
    aug_budget.month_summary()  #groceries 120 eating out 85
                                #no goals
    # Print daily summary for Sept 1
    sept_budget.daily_summary("2025-09-01") #groceries ah 120
                                            #eating out mcd 15

    # Export CSV
    sept_budget.export_csv("september_budget.csv")

    # -----------------------------------YearlyBudget-----------------------------------------
    # Set a yearly savings goal
    year_budget.set_savings_goal(5000)

    # Add incomes
    year_budget.add_income(3000, "Full-time Job")
    year_budget.add_income(2000, "Freelance")
    year_budget.add_income(1500, "Gift")

    # Add expenses (spread across the year)
    year_budget.add_expense("Groceries", "Walmart", 120, "2025-01-05")
    year_budget.add_expense("Groceries", "Trader Joe's", 80, "2025-03-10")
    year_budget.add_expense("Eating Out", "McDonalds", 15, "2025-02-01")
    year_budget.add_expense("Eating Out", "Starbucks", 10, "2025-09-12")
    year_budget.add_expense("Travel", "Uber", 50, "2025-05-07")
    year_budget.add_expense("Travel", "Train", 100, "2025-08-20")
    year_budget.add_expense("Gym", "Local Gym", 60, "2025-01-15")

    # summarize
    year_budget.summary("2025-09-01") #income 6500
                                      #groceries 440
                                      #gym 60
                                      #eating out 115
                                      #travel 150
                                      #total expenses 440+60+115+150=765

    # Export CSV
    year_budget.export_csv("2025_budget.csv")
