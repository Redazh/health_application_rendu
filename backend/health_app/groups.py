# health_app/graph.py
from django.contrib.auth.models import User
import networkx as nx
from networkx.algorithms import community
from health_app.models import Friendship

# Global graph variable
G = nx.Graph()

def build_graph():
    """
    Build the friendship graph using only database information.
    Each user is added as a node with a 'Cluster' attribute obtained from their profile.
    Friendships are added using the Friendship.get_friends(user_id) method.
    """
    # Retrieve all users from the database
    users = User.objects.all()
    print("[DEBUG] Total users retrieved:", users.count())

    # Add nodes to the graph, each with a 'Cluster' attribute.
    for user in users:
        try:
            cluster = user.profile.assigned_cluster  # Assuming profile has a field 'assigned_cluster'
        except AttributeError:
            cluster = 0  # Default value if not defined
        G.add_node(user.id, Cluster=cluster)
        print(f"[DEBUG] Added node for user {user.id} with cluster {cluster}")

    # Add edges for friendships based on the friendship model.
    for user in users:
        # Use the user's primary key (user.id) here
        friend_ids = Friendship.get_friends(user.id)
        print(f"[DEBUG] For user {user.id} found friend_ids: {friend_ids}")
        for friend_id in friend_ids:
            print(f"[DEBUG] Processing friend_id {friend_id} for user {user.id}")
            try:
                friend = User.objects.get(id=friend_id)
                try:
                    friend_cluster = friend.profile.assigned_cluster
                except AttributeError:
                    friend_cluster = 0
                print(f"[DEBUG] Found friend {friend.username} with cluster {friend_cluster}")
            except User.DoesNotExist:
                print(f"[DEBUG] Friend with id {friend_id} not found, skipping.")
                continue  # Skip if the friend is not found in the database

            # Set a stronger weight if both users belong to the same cluster
            weight = 1.0 if cluster == friend_cluster else 1.0
            print(f"[DEBUG] Adding edge from {user.id} to {friend_id} with weight {weight}")
            G.add_edge(user.id, friend_id, weight=weight)

    # Detect communities using the Louvain method
    communities = community.louvain_communities(G, weight='weight', resolution=1.0)
    community_dict = {}
    for i, community_set in enumerate(communities):
        print(f"[DEBUG] Community {i} contains nodes: {community_set}")
        for node in community_set:
            community_dict[node] = i
    nx.set_node_attributes(G, community_dict, 'Community')
    print("[DEBUG] Graph built with communities assigned.")

def get_graph():
    """
    Returns the global friendship graph.
    If the graph is not yet built, it will be built now.
    """
    if not G.nodes:
        build_graph()
    return G

from django.contrib.auth.models import User

def get_group_members(user_id):
    """
    Returns the group of very close-knit friends (usernames) for a given user.
    In this example, we return the names of all users that share the same community.
    """
    graph = get_graph()
    if user_id not in graph.nodes:
        print(f"[DEBUG] User {user_id} not found in graph.")
        return []
    community_id = graph.nodes[user_id].get("Community")
    # Get the IDs of all users in the same community
    group_member_ids = [
        node for node, data in graph.nodes(data=True) if data.get("Community") == community_id
    ]
    # Look up the usernames for these IDs
    group_member_names = []
    for member_id in group_member_ids:
        try:
            user_obj = User.objects.get(id=member_id)
            group_member_names.append(user_obj.username)
        except User.DoesNotExist:
            print(f"[DEBUG] User with id {member_id} not found in the database.")
    print(f"[DEBUG] get_group_members({user_id}) returned: {group_member_names}")
    return group_member_names
