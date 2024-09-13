import math

A = [
        14.234381896570113,
        53.30257998520777,
        257.61791493049293
      ]
B =   [
        48.452153772744495,
        48.68450060323472,
        273.4866713610355
      ]
# Calculate Euclidean distance
distance = math.sqrt((B[0] - A[0]) ** 2 + (B[1] - A[1]) ** 2 + (B[2] - A[2]) ** 2)

print("Distance between points A and B:", distance)
