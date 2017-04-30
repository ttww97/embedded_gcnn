from ..segmentation.adjacency import segmentation_adjacency
from ..graph.embedded_coarsening import coarsen_embedded_adj
from ..graph.distortion import perm_features
from ..tf.convert import sparse_to_tensor


def preprocess(image,
               segmentation_algorithm,
               feature_extraction_algorithm,
               levels,
               scale_invariance=False,
               stddev=1):

    segmentation = segmentation_algorithm(image)

    adj, points, mass = segmentation_adjacency(segmentation)

    adjs_dist, adjs_rad, perm = coarsen_embedded_adj(points, mass, adj, levels,
                                                     scale_invariance, stddev)

    features = feature_extraction_algorithm(segmentation, image)
    features = perm_features(features, perm)

    adjs_dist = [sparse_to_tensor(A) for A in adjs_dist]
    adjs_rad = [sparse_to_tensor(A) for A in adjs_rad]

    return features, adjs_dist, adjs_rad


def preprocess_fixed(segmentation_algorithm,
                     feature_extraction_algorithm,
                     levels,
                     scale_invariance=False,
                     stddev=1):
    def _preprocess(image):
        return preprocess(image, segmentation_algorithm,
                          feature_extraction_algorithm, levels,
                          scale_invariance, stddev)

    return _preprocess