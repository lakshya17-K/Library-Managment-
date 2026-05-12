class FineStrategy:

    @staticmethod
    def calculate_fine(days):

        free_days = 7

        if days <= free_days:
            return 0

        return (days - free_days) * 5
