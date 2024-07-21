import os
import pycolmap
import numpy as np
import torchvision
from gaustudio.pipelines import initializers
from gaustudio.pipelines.initializers.base import BaseInitializer
import math

def fibonacci_sphere(samples=1):
    points = []
    phi = math.pi * (3. - math.sqrt(5.))  # golden angle in radians

    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2 # y goes from 1 to -1
        radius = math.sqrt(1 - y**2) # radius at y

        theta = phi * i # golden angle increment

        x = math.cos(theta) * radius
        z = math.sin(theta) * radius

        points.append((x,y,z))

    return points

def euclidean_distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def inverse_sigmoid(x):
    return np.log(x / (1 - x))

@initializers.register('gaussiansky')
class GaussianSkyInitializer(BaseInitializer):
    def __init__(self, initializer_config):
        super().__init__(initializer_config)
        self.resolution = initializer_config.get('resolution', 500)
        self.radius = initializer_config.get('radius', 1.0)

    def build_model(self, model):
        num_background_points = self.resolution**2
        xyz = fibonacci_sphere(num_background_points)
        xyz = np.array(xyz) * self.radius

        # TODO: add rgb generation from dataset
        
        dist = euclidean_distance(xyz[0], xyz[1])
        dist = math.log(dist)
        scale = np.ones_like(xyz) * dist
        opacity = inverse_sigmoid(np.ones((xyz.shape[0], 1)))
        try:
            model.create_from_attribute(xyz=xyz, scale=scale, opacity=opacity)
        except Exception as e:
            print(f"Failed to update point cloud: {e}")
            raise
        return model