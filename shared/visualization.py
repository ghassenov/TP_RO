import matplotlib.pyplot as plt

def plot_mailbox_solution(demand_points, facilities, radius, selected_facilities):
    plt.figure(figsize=(7, 7))

    xs = [p["x"] for p in demand_points]
    ys = [p["y"] for p in demand_points]
    plt.scatter(xs, ys, label="Population Points", s=40)

    fx = [f["x"] for f in facilities]
    fy = [f["y"] for f in facilities]
    plt.scatter(fx, fy, marker="^", label="Candidate Sites", s=80)

    sel_fx = [facilities[i]["x"] for i in selected_facilities]
    sel_fy = [facilities[i]["y"] for i in selected_facilities]
    plt.scatter(sel_fx, sel_fy, marker="*", label="Selected Mailboxes", s=150)

    for i in selected_facilities:
        circ = plt.Circle((facilities[i]["x"], facilities[i]["y"]), radius,
                          color='gray', alpha=0.2)
        plt.gca().add_patch(circ)

    plt.title("Optimal Mailbox Location")
    plt.grid()
    plt.legend()
    plt.show()
