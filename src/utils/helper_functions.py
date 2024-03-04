# -*- coding: utf-8 -*-
"""
This module contains utility functions for mapping and converting arrays.

Functions:
- map_1d_array: Map the elements of a 1D array using a mapper dictionary.
- map_2d_array: Map the elements of a 2D array using a mapper dictionary.
- map_array: Map the elements of a 1D or 2D array using a mapper dictionary.
- map_multiidx_to_iloc: Convert a multi-index array to integer-based indexing.

@Author: Adrien Perello
@Date: 28.02.2024
"""

from functools import reduce
from operator import mul

import numpy as np


def map_1d_array(arr, mapper):
    """
    Map the elements of a 1D array using a mapper dictionary.

    Args:
        arr (ndarray): The input array.
        mapper (dict): A dictionary mapping the elements of the array to their corresponding values.

    Returns:
        ndarray: The mapped 1D array.
    """
    return np.vectorize(mapper.__getitem__)(arr)


def map_2d_array(arr, mapper, keys):
    """
    Map the elements of a 2D array using a mapper dictionary.

    Args:
        arr (ndarray): The input 2D array.
        mapper (dict): A dictionary mapping the elements of each column to their corresponding values.
        keys (list): List of keys representing the columns of the array (in the right order)

    Returns:
        ndarray: The mapped 2D array.
    """
    res = [map_1d_array(arr=arr[:, i], mapper=mapper[keys[i]]) for i in range(arr.shape[1])]
    return np.vstack(res).T


def map_array(arr, mapper, keys):
    """
    Map the elements of a 1D or 2D array using a mapper dictionary.

    Args:
        arr (numpy.ndarray): The input array to be mapped.
        mapper (dict): The dictionary to be applied to each element of the array.
        keys (list): List of keys to be used for mapping the elements of the array.
            Note: the keys should be in the right order.

    Raises:
        ValueError: If the input array is not 1D or 2D.

    Returns:
        numpy.ndarray: The mapped array.
    """
    if arr.ndim == 1:
        return map_1d_array(arr, mapper)
    if arr.ndim == 2:
        return map_2d_array(arr, mapper, keys)
    raise ValueError("Array must be 1D or 2D")


def map_multiidx_to_iloc(arr, shape):
    """Convert a list of points in a multiindex to their corresponding integer-based indices.

    Args:
        arr (ndarray[int]): Array of integers representing the location along each dimension of multiple points
        shape (tuple): The dimensional space

    Returns:
        ndarray: The integer-based indices = (a0, a1, ..., an-1, an), with:
            a0 = shape[1] * shape[2] * ... * shape[n] * 1,
            a1 = shape[2] * ... * shape[n] * 1,
            an-1 = shape[n]
            an = 1
    """
    coeff = np.array([reduce(mul, shape[i + 1 :]) if i + 1 < len(shape) else 1 for i, _ in enumerate(shape)])
    try:
        return (coeff * arr).sum(axis=1)
    except np.AxisError:  # if target was a 1d array
        return (coeff * arr).sum()
