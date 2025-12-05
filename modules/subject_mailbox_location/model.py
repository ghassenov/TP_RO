class MailboxLocationModel:
    def __init__(self, demand_points, facilities, radius, num_mailboxes):
        self.demand_points = demand_points
        self.facilities = facilities
        self.radius = radius
        self.num_mailboxes = num_mailboxes

    def distance(self, p, f):
        return ((p["x"] - f["x"])**2 + (p["y"] - f["y"])**2) ** 0.5
