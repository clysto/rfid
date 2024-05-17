import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin


class DPC(ClusterMixin, BaseEstimator):
    def __init__(self, n_clusters, dc=None, filter_halo=False):
        self.n_clusters = n_clusters
        self.dc = dc
        self.filter_halo = filter_halo

    def estimate_dc(self):
        n = np.shape(self.dists_)[0]
        tt = np.reshape(self.dists_, n * n)
        position = int(n * (n - 1) * 0.02)
        dc = np.sort(tt)[position + n]
        return dc

    def fit(self, X):
        N = X.shape[0]
        # calc distance matrix
        self.dists_ = np.abs(X[:, np.newaxis] - X)
        if self.dc is None:
            self.dc = self.estimate_dc()

        # calc local density using gaussian kernel
        self.rhos_ = np.sum(np.exp(-((self.dists_ / self.dc) ** 2)), axis=1) - 1

        # calc delta and nearest neighbor
        self.deltas_ = np.zeros(N)
        nearest_neighbors = np.zeros(N)
        ordrho = np.argsort(-self.rhos_)
        for i, index in enumerate(ordrho):
            if i == 0:
                continue
            index_higher_rho = ordrho[:i]
            self.deltas_[index] = np.min(self.dists_[index, index_higher_rho])
            index_nn = np.argmin(self.dists_[index, index_higher_rho])
            nearest_neighbors[index] = index_higher_rho[index_nn]
        # set delta of the point with highest density to the maximum delta
        self.deltas_[ordrho[0]] = np.max(self.deltas_)

        index_center = np.argsort(-self.rhos_ * self.deltas_)[: self.n_clusters]
        self.labels_ = np.full(N, -1, dtype=np.intp)

        for i, center in enumerate(index_center):
            self.labels_[center] = i
        for i, index in enumerate(ordrho):
            if self.labels_[index] == -1:
                self.labels_[index] = self.labels_[int(nearest_neighbors[index])]
        if self.filter_halo:
            self.labels_[self.deltas_ > self.dc] = -1
            for i, center in enumerate(index_center):
                self.labels_[center] = i
        return self

    def fit_predict(self, X):
        self.fit(X)
        return self.labels_
