class MailboxLocationModel:
    def __init__(self, demand_points, num_mailboxes, radius, 
                 costs=None, budgets=None, capacities=None):
        self.demand_points = demand_points
        self.num_mailboxes = num_mailboxes
        self.radius = radius
        self.costs = costs if costs else [1.0] * num_mailboxes
        self.budgets = budgets
        self.capacities = capacities