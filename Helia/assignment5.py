from abc import ABC, abstractmethod

class Budget(ABC):
    def __init__(self):
        # Each expense is a dict: {"category": str, "cost": float}
        self.expenses = []

    def add_expense(self, category, cost):
        self.expenses.append({
            "category": category,
            "cost": cost
        })

    @abstractmethod
    def summary(self, date):
        """Abstract method: subclasses must implement their own summary printing."""
        pass

class MonthlyBudget(Budget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def summary(self):
        self.month_summary()

    def month_summary(self):
        print(f"\n📅 Monthly Budget Summary")
        print("-" * 65)
        print(f"{'Category':<15}{'Spent':<10}")
        print("-" * 65)

        for e in self.expenses:
            print(f"{e['category']:<15}${e['cost']:<9.2f}")
        print("-" * 65)

    def add_expense(self, category, cost):
        Budget.add_expense(self,category, cost)
        # same as 
        # super().add_expense(category, cost)
        if self.parent:
            self.parent.add_expense(category, cost)


class YearlyBudget(Budget):
    """Manage a yearly budget with incomes, expenses, and savings goal."""

    def __init__(self):
        super().__init__()

    def summary(self):
        self.year_summary()

    def year_summary(self):
        print(f"\n📅 Yearly Budget Summary")
        print("-" * 65)
        print(f"{'Category':<15}{'Spent':<10}")
        print("-" * 65)

        for e in self.expenses:
            print(f"{e['category']:<15}${e['cost']:<9.2f}")
        print("-" * 65)

if __name__ == "__main__":
    year_budget = YearlyBudget()
    aug_budget = MonthlyBudget(parent=year_budget)
    sept_budget = MonthlyBudget(parent=year_budget)

    aug_budget.add_expense("Eating Out", 50)
    aug_budget.add_expense("Groceries", 100)
    aug_budget.add_expense("Groceries", 30)
    aug_budget.add_expense("Travel", 18)
    aug_budget.add_expense("Travel", 2)

    sept_budget.add_expense("Eating Out", 15)
    sept_budget.add_expense("Groceries", 80)
    sept_budget.add_expense("Groceries", 120)
    sept_budget.add_expense("Travel", 50)
    sept_budget.add_expense("Relax", 50)

    year_budget.add_expense("Groceries", 200)

    aug_budget.summary()
    sept_budget.summary()
    year_budget.summary()
