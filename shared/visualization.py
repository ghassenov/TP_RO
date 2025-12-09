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

def plot_antenna_solution(users, selected_sites, coverage_radius):
    """Visualiser la solution de placement d'antennes"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

    # Couleurs - use tuples not strings for RGBA
    colors = {
        'users': '#3498db',
        'covered_users': '#2ecc71',
        'uncovered_users': '#e74c3c',
        'sites': '#e74c3c',
        'selected_sites': '#f39c12',
        'coverage': (0.95, 0.61, 0.07, 0.1)  # RGBA tuple: (r,g,b,a)
    }

    # Tracer les utilisateurs
    user_x = [u['x'] for u in users]
    user_y = [u['y'] for u in users]
    user_demands = [u.get('demand', 1) for u in users]

    # Taille proportionnelle à la demande
    max_demand = max(user_demands) if user_demands else 1
    user_sizes = [20 + 80 * (d / max_demand) for d in user_demands]

    # Identifier les utilisateurs couverts
    covered_users = set()
    for site in selected_sites:
        if site.get('built', False):
            site_x, site_y = site['x'], site['y']
            # Vérifier quels utilisateurs sont dans le rayon
            for i, user in enumerate(users):
                distance = ((user['x'] - site_x)**2 + (user['y'] - site_y)**2) ** 0.5
                if distance <= coverage_radius:
                    covered_users.add(i)

    # Tracer utilisateurs non couverts
    uncovered_indices = [i for i in range(len(users)) if i not in covered_users]
    if uncovered_indices:
        unc_x = [user_x[i] for i in uncovered_indices]
        unc_y = [user_y[i] for i in uncovered_indices]
        unc_sizes = [user_sizes[i] for i in uncovered_indices]
        ax.scatter(unc_x, unc_y, s=unc_sizes, color=colors['uncovered_users'],
                  alpha=0.6, label=f'Non Couverts ({len(uncovered_indices)})', zorder=2)

    # Tracer utilisateurs couverts
    if covered_users:
        cov_x = [user_x[i] for i in covered_users]
        cov_y = [user_y[i] for i in covered_users]
        cov_sizes = [user_sizes[i] for i in covered_users]
        ax.scatter(cov_x, cov_y, s=cov_sizes, color=colors['covered_users'],
                  alpha=0.8, label=f'Couverts ({len(covered_users)})', zorder=3)

    # Tracer les sites sélectionnés
    for site in selected_sites:
        if site.get('built', False):
            # Site avec antenne
            ax.scatter(site['x'], site['y'], s=300, marker='^',
                      color=colors['selected_sites'], edgecolors='black',
                      linewidth=2, label='Antenne' if not ax.get_legend() else "", zorder=5)

            # Zone de couverture
            circle = plt.Circle((site['x'], site['y']), coverage_radius,
                              fill=True, alpha=0.1, color=colors['selected_sites'])  # Use hex color
            ax.add_patch(circle)

            # Ligne de couverture
            circle_edge = plt.Circle((site['x'], site['y']), coverage_radius,
                                   fill=False, alpha=0.5, color=colors['selected_sites'],
                                   linestyle='--', linewidth=1)
            ax.add_patch(circle_edge)

            # Étiquette du site
            capacity = site.get('capacity', 0)
            num_users = site.get('num_users', 0)
            label = f"{site.get('name', f'Site')}\nCap: {capacity}\nUsers: {num_users}"

            ax.annotate(label,
                       xy=(site['x'], site['y']),
                       xytext=(0, 15),
                       textcoords='offset points',
                       ha='center', va='center',
                       fontsize=8,
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='white',
                                alpha=0.9,
                                edgecolor='black'))

            # Lignes vers les utilisateurs affectés
            for user in site.get('assigned_users', []):
                ax.plot([site['x'], user['x']], [site['y'], user['y']],
                       color=colors['selected_sites'], alpha=0.3,
                       linewidth=1, linestyle='-', zorder=1)

    # Configuration
    ax.set_xlabel('Position X', fontsize=12, fontweight='bold')
    ax.set_ylabel('Position Y', fontsize=12, fontweight='bold')
    ax.set_title('Placement Optimal des Antennes Télécom',
                fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_aspect('equal', adjustable='box')

    # Légende
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Utilisateur Couvert',
              markerfacecolor=colors['covered_users'], markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Utilisateur Non Couvert',
              markerfacecolor=colors['uncovered_users'], markersize=10),
        Line2D([0], [0], marker='^', color='w', label='Antenne',
              markerfacecolor=colors['selected_sites'], markersize=12, markeredgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)

    plt.tight_layout()
    return fig


import matplotlib.pyplot as plt
import networkx as nx


def plot_mis_solution(tasks, conflicts, selected_tasks):
    """Visualiser la solution de l'Ensemble Indépendant Maximum"""
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100)

    # Créer le graphe
    G = nx.Graph()

    # Ajouter les nœuds (tâches)
    for task in tasks:
        G.add_node(task['id'],
                   label=task.get('name', f"T{task['id']}"),
                   duration=task.get('duration', 1),
                   priority=task.get('priority', 1),
                   selected=any(t['id'] == task['id'] for t in selected_tasks))

    # Ajouter les arêtes (conflits)
    for i, j in conflicts:
        if i < len(tasks) and j < len(tasks):
            G.add_edge(i, j)

    # Positions des nœuds (layout circulaire)
    pos = nx.circular_layout(G)

    # Couleurs
    colors = {
        'selected': '#2ecc71',    # Vert pour les tâches sélectionnées
        'unselected': '#e74c3c',  # Rouge pour les autres
        'conflict': '#7f8c8d',    # Gris pour les arêtes
        'highlight': '#f39c12'    # Orange pour mettre en évidence
    }

    # Tracer les arêtes (conflits)
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=1, edge_color=colors['conflict'])

    # Tracer les nœuds non sélectionnés
    unselected_nodes = [node for node in G.nodes() if not G.nodes[node]['selected']]
    if unselected_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=unselected_nodes,
                              node_color=colors['unselected'],
                              node_size=700, alpha=0.7)

    # Tracer les nœuds sélectionnés (plus grands)
    selected_nodes = [node for node in G.nodes() if G.nodes[node]['selected']]
    if selected_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=selected_nodes,
                              node_color=colors['selected'],
                              node_size=1000, alpha=0.9,
                              edgecolors='black', linewidths=2)

    # Étiquettes des nœuds
    labels = {}
    for node in G.nodes():
        task_data = G.nodes[node]
        labels[node] = f"{task_data['label']}\nP:{task_data['priority']}"

    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold')

    # Titre et légende
    ax.set_title("Graphe d'Incompatibilité - Ensemble Indépendant Maximum",
                fontsize=14, fontweight='bold', pad=20)

    # Légende
    from matplotlib.patches import Circle
    legend_elements = [
        Circle((0, 0), 1, color=colors['selected'], label='Tâche sélectionnée'),
        Circle((0, 0), 1, color=colors['unselected'], label='Tâche non sélectionnée'),
        plt.Line2D([0], [0], color=colors['conflict'], lw=2, label='Conflit')
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)

    ax.axis('off')
    plt.tight_layout()

    return fig

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon


def plot_triangulation_solution(points, selected_triangles, title="Truss Structure"):
    """
    Simple triangulation plot
    """
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot points
    if points:
        x_coords = [p['x'] for p in points]
        y_coords = [p['y'] for p in points]
        ax.scatter(x_coords, y_coords, c='blue', s=100, zorder=5, label='Points')

        # Add point labels
        for i, p in enumerate(points):
            ax.annotate(str(i), (p['x'], p['y']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold')

    # Plot selected triangles
    if selected_triangles:
        for tri in selected_triangles:
            vertices = tri['vertices']
            if len(vertices) == 3:
                # Get point coordinates
                tri_points = []
                for v in vertices:
                    if v < len(points):
                        tri_points.append([points[v]['x'], points[v]['y']])

                if len(tri_points) == 3:
                    tri_points.append(tri_points[0])  # Close the triangle
                    x_vals = [p[0] for p in tri_points]
                    y_vals = [p[1] for p in tri_points]

                    # Plot triangle with color based on cost
                    cost = tri.get('cost', 1.0)
                    alpha = 0.3 + 0.4 * (cost / max(1.0, cost))
                    ax.fill(x_vals, y_vals, alpha=alpha, edgecolor='red',
                           linewidth=2, label=f'Cost: {cost:.1f}')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    plt.tight_layout()
    return fig
