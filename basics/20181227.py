# -*- coding: utf-8 -*-
"""
Created on Thu Dec 27 16:58:32 2018

@author: sgiraldo
"""
import heapq
import random
import time

def createArray():
    array = list(range( 10 * 1000 * 1000 ))
    random.shuffle( array )
    return array

def linearSearch( bigArray, k ):
    return sorted(bigArray, reverse=True)[:k]

def heapSearch( bigArray, k ):
    heap = []
    for item in bigArray:
        # If we have not yet found k items, or the current item is larger than
        # the smallest item on the heap,
        if len(heap) < k or item > heap[0]:
            # If heap is full, remove the smallest element on the heap.
            if len(heap) == k: heapq.heappop( heap )
            # add the current element as the new smallest.
            heapq.heappush( heap, item )
    return heap

def heapSearchBuiltin( bigArray, k ):
    return heapq.nlargest( k, bigArray )
        
start = time.time()
bigArray = createArray()
print("Creating array took %g s" % (time.time() - start))

start = time.time()
print(linearSearch( bigArray, 10 ))
print("Linear search took %g s" % (time.time() - start))

start = time.time()
print(heapSearch( bigArray, 10 ))
print("Heap search took %g s" % (time.time() - start))

start = time.time()
print(heapSearchBuiltin( bigArray, 10 ))
print("Heap search builtin took %g s" % (time.time() - start))