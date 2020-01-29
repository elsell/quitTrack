"""
elsell
github.com/elsell

Sample Use for MosquitoTracker Class
Jan 2020
"""

from mosquitoTracker import MosquitoTracker

# Init tracker (using the 2nd webcam input)
mt = MosquitoTracker(1)

# Start Capturing (and displaying) video & tracking data
mt.Capture()
