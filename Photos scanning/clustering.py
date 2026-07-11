# clustering.py

import numpy as np
import hdbscan
from sklearn.preprocessing import normalize
from collections import defaultdict


class FaceClusterer:

    def __init__(
        self,
        min_cluster_size=2,
        min_samples=1,
        metric='euclidean'
    ):

        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.metric = metric

    # =====================================================
    # NORMALIZE EMBEDDINGS
    # =====================================================

    @staticmethod
    def normalize_embeddings(embeddings):

        embeddings = np.array(embeddings)

        normalized = normalize(embeddings)

        return normalized

    # =====================================================
    # CLUSTER
    # =====================================================

    def cluster(self, embeddings):

        if len(embeddings) == 0:
            return np.array([])

        embeddings = self.normalize_embeddings(
            embeddings
        )

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric=self.metric,
            prediction_data=True
        )

        labels = clusterer.fit_predict(embeddings)

        return labels

    # =====================================================
    # BUILD CLUSTER MAP
    # =====================================================

    @staticmethod
    def build_cluster_map(labels):

        cluster_map = defaultdict(list)

        for idx, label in enumerate(labels):

            if label == -1:
                continue

            cluster_map[int(label)].append(idx)

        return dict(cluster_map)

    # =====================================================
    # PRINT CLUSTER SUMMARY
    # =====================================================

    @staticmethod
    def print_cluster_summary(labels):

        unique_labels = set(labels)

        if -1 in unique_labels:
            unique_labels.remove(-1)

        print("\n" + "=" * 50)
        print("CLUSTER SUMMARY")
        print("=" * 50)

        print(f"Total clusters: {len(unique_labels)}")

        for label in sorted(unique_labels):

            count = np.sum(labels == label)

            print(f"Person {label}: {count} faces")

        noise_count = np.sum(labels == -1)

        print(f"\nNoise faces: {noise_count}")

    # =====================================================
    # GET LARGEST CLUSTERS
    # =====================================================

    @staticmethod
    def largest_clusters(labels, top_n=10):

        cluster_sizes = {}

        for label in labels:

            if label == -1:
                continue

            cluster_sizes[label] = (
                cluster_sizes.get(label, 0) + 1
            )

        sorted_clusters = sorted(
            cluster_sizes.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return sorted_clusters[:top_n]

    # =====================================================
    # REMOVE SMALL CLUSTERS
    # =====================================================

    @staticmethod
    def remove_small_clusters(labels, min_size=2):

        cluster_sizes = {}

        for label in labels:

            if label == -1:
                continue

            cluster_sizes[label] = (
                cluster_sizes.get(label, 0) + 1
            )

        cleaned_labels = []

        for label in labels:

            if label == -1:
                cleaned_labels.append(-1)
                continue

            if cluster_sizes[label] < min_size:
                cleaned_labels.append(-1)
            else:
                cleaned_labels.append(label)

        return np.array(cleaned_labels)

    # =====================================================
    # CLUSTER STATISTICS
    # =====================================================

    @staticmethod
    def get_statistics(labels):

        total_faces = len(labels)

        unique_clusters = len(
            set([x for x in labels if x != -1])
        )

        noise_faces = np.sum(labels == -1)

        clustered_faces = total_faces - noise_faces

        return {
            'total_faces': total_faces,
            'total_people': unique_clusters,
            'clustered_faces': int(clustered_faces),
            'noise_faces': int(noise_faces),
            'clustering_ratio': (
                clustered_faces / total_faces
                if total_faces > 0 else 0
            )
        }


# =========================================================
# TESTING
# =========================================================

if __name__ == "__main__":

    # Simulated embeddings

    embeddings = np.random.rand(100, 512)

    clusterer = FaceClusterer(
        min_cluster_size=2,
        min_samples=1
    )

    labels = clusterer.cluster(embeddings)

    clusterer.print_cluster_summary(labels)

    stats = clusterer.get_statistics(labels)

    print("\nStatistics:")
    print(stats)

    print("\nLargest clusters:")
    print(clusterer.largest_clusters(labels))