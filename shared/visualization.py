import matplotlib.patches as patches
import matplotlib.pyplot as plt


def plot_mailbox_solution(demand_points, mailbox_locations, coverage_info, radius):
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

    colors = {
        'demand': '#2E86AB',
        'mailbox': '#E63946',
        'coverage': '#F4A261',
        'covered_demand': '#1D3557',
        'uncovered_demand': '#8D99AE'
    }

    demand_x = [p.get('x', 0) for p in demand_points]
    demand_y = [p.get('y', 0) for p in demand_points]
    populations = [p.get('population', 1) for p in demand_points]
    demands = [p.get('demand', 1) for p in demand_points]

    max_pop = max(populations) if populations else 1
    max_demand = max(demands) if demands else 1
    demand_sizes = [40 + 200 * (pop/max_pop) for pop in populations]
    demand_alphas = [0.3 + 0.7 * (d/max_demand) for d in demands]

    covered_indices = [i for i, info in enumerate(coverage_info)
                      if info.get('coverage_level', 0) > 0]
    uncovered_indices = [i for i in range(len(demand_points))
                        if i not in covered_indices]

    if uncovered_indices:
        unc_x = [demand_x[i] for i in uncovered_indices]
        unc_y = [demand_y[i] for i in uncovered_indices]
        unc_sizes = [demand_sizes[i] for i in uncovered_indices]
        unc_alphas = [demand_alphas[i] for i in uncovered_indices]
        ax.scatter(unc_x, unc_y, s=unc_sizes, alpha=unc_alphas,
                  color=colors['uncovered_demand'], edgecolors='white', linewidth=1,
                  label=f'Uncovered ({len(uncovered_indices)})', zorder=2)

    if covered_indices:
        cov_x = [demand_x[i] for i in covered_indices]
        cov_y = [demand_y[i] for i in covered_indices]
        cov_sizes = [demand_sizes[i] for i in covered_indices]
        cov_alphas = [demand_alphas[i] for i in covered_indices]
        ax.scatter(cov_x, cov_y, s=cov_sizes, alpha=cov_alphas,
                  color=colors['covered_demand'], edgecolors='white', linewidth=1.5,
                  label=f'Covered ({len(covered_indices)})', zorder=3)

    mailbox_colors = []
    for i, loc in enumerate(mailbox_locations):
        if loc.get('built', False):
            color = plt.cm.RdYlBu(i / max(1, len(mailbox_locations)))
            mailbox_colors.append(color)

            ax.scatter(loc['x'], loc['y'], s=400, marker='*',
                      color=color, edgecolors='black', linewidth=2,
                      label=f'Mailbox {i+1}' if i == 0 else "", zorder=5)

            coverage = patches.Circle(
                (loc['x'], loc['y']), radius,
                fill=True, alpha=0.15, color=color,
                linestyle='--', linewidth=1
            )
            ax.add_patch(coverage)

            boundary = patches.Circle(
                (loc['x'], loc['y']), radius,
                fill=False, alpha=0.8, color=color,
                linewidth=2, linestyle='-'
            )
            ax.add_patch(boundary)

            ax.annotate(f'M{i+1}',
                       xy=(loc['x'], loc['y']),
                       xytext=(0, 10),
                       textcoords='offset points',
                       ha='center', va='center',
                       fontsize=10, fontweight='bold',
                       color='black',
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='white',
                                alpha=0.8,
                                edgecolor='black'))

    for i, info in enumerate(coverage_info):
        if info.get('coverage_level', 0) > 1:
            ax.annotate(f'{int(info["coverage_level"])}',
                       xy=(demand_x[i], demand_y[i]),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8, fontweight='bold',
                       color='red',
                       bbox=dict(boxstyle='circle,pad=0.2',
                                facecolor='white',
                                alpha=0.8))

    for i, loc in enumerate(mailbox_locations):
        if loc.get('built', False):
            for info in coverage_info:
                if i in info.get('served_by', []):
                    point_idx = info.get('point', 0)
                    ax.plot([loc['x'], demand_x[point_idx]],
                           [loc['y'], demand_y[point_idx]],
                           color=mailbox_colors[i], alpha=0.3,
                           linewidth=1, linestyle=':', zorder=1)

    stats_text = f"""
    Statistics:
    • Total Points: {len(demand_points)}
    • Covered: {len(covered_indices)} ({len(covered_indices)/len(demand_points)*100:.1f}%)
    • Mailboxes: {sum(1 for loc in mailbox_locations if loc.get('built', False))}/{len(mailbox_locations)}
    • Radius: {radius:.1f}
    """

    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round',
                     facecolor='white',
                     alpha=0.9,
                     edgecolor='gray'))

    ax.set_xlabel('X Coordinate', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y Coordinate', fontsize=12, fontweight='bold')
    ax.set_title('Mailbox Location Optimization', fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_aspect('equal', adjustable='box')

    all_x = demand_x + [loc['x'] for loc in mailbox_locations if loc.get('built', False)]
    all_y = demand_y + [loc['y'] for loc in mailbox_locations if loc.get('built', False)]

    if all_x and all_y:
        x_padding = max(radius, (max(all_x) - min(all_x)) * 0.1)
        y_padding = max(radius, (max(all_y) - min(all_y)) * 0.1)
        ax.set_xlim(min(all_x) - x_padding, max(all_x) + x_padding)
        ax.set_ylim(min(all_y) - y_padding, max(all_y) + y_padding)

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc='upper right', framealpha=0.9, fontsize=9)

    plt.tight_layout()
    return fig

def plot_telecom_solution(nodes, selected_links, demands=None):
    """Visualiser la solution du réseau de télécom"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

    # Tracer les nœuds
    node_x = [node['x'] for node in nodes]
    node_y = [node['y'] for node in nodes]
    node_names = [node['name'] for node in nodes]

    ax.scatter(node_x, node_y, s=300, c='lightblue', edgecolors='darkblue', linewidth=2, zorder=5)

    # Annoter les nœuds
    for i, (x, y, name) in enumerate(zip(node_x, node_y, node_names)):
        ax.annotate(f"{name}\n({i})",
                   xy=(x, y),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center', va='center',
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Tracer les liaisons
    for link in selected_links:
        if link.get('built', False):
            from_node = link['from']
            to_node = link['to']

            # Trouver les coordonnées
            from_x, from_y = nodes[from_node]['x'], nodes[from_node]['y']
            to_x, to_y = nodes[to_node]['x'], nodes[to_node]['y']

            # Largeur proportionnelle à la capacité
            capacity = link.get('capacity', 100)
            linewidth = 1 + (capacity / 1000) * 3

            # Couleur proportionnelle à l'utilisation
            utilization = link.get('utilization', 0)
            if utilization < 0.5:
                color = 'green'
            elif utilization < 0.8:
                color = 'orange'
            else:
                color = 'red'

            # Tracer la ligne
            ax.plot([from_x, to_x], [from_y, to_y],
                   color=color, linewidth=linewidth, alpha=0.7, zorder=3)

            # Ajouter l'étiquette
            mid_x = (from_x + to_x) / 2
            mid_y = (from_y + to_y) / 2

            label = f"{capacity}G\n({utilization*100:.0f}%)"
            ax.annotate(label,
                       xy=(mid_x, mid_y),
                       xytext=(0, 0),
                       textcoords='offset points',
                       ha='center', va='center',
                       fontsize=8,
                       bbox=dict(boxstyle='round,pad=0.2',
                                facecolor='white',
                                alpha=0.8,
                                edgecolor='gray'))

    # Configuration du graphique
    ax.set_xlabel('Position X', fontsize=12, fontweight='bold')
    ax.set_ylabel('Position Y', fontsize=12, fontweight='bold')
    ax.set_title('Conception Optimale du Réseau Fibre Optique',
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_aspect('equal', adjustable='box')

    # Légende
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='green', lw=2, label='Utilisation < 50%'),
        Line2D([0], [0], color='orange', lw=2, label='Utilisation 50-80%'),
        Line2D([0], [0], color='red', lw=2, label='Utilisation > 80%'),
        Line2D([0], [0], marker='o', color='w', label='Nœud',
              markerfacecolor='lightblue', markersize=10, markeredgecolor='darkblue')
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)

    plt.tight_layout()
    return fig
