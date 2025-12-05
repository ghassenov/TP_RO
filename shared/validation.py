def validate_mailbox_input(demand_points, num_mailboxes, radius):
    if num_mailboxes <= 0:
        raise ValueError("Number of mailboxes must be positive.")

    if radius <= 0:
        raise ValueError("Radius must be positive.")

    if len(demand_points) == 0:
        raise ValueError("No demand points provided.")
