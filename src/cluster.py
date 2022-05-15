from sklearn.cluster import AgglomerativeClustering
import itertools
import numpy as np
from scipy import stats
import pandas as pd
from src.utils import wrap


def map_cluster(cluster, coordText):
	words = []
	cluster = cluster.tolist()
	cluster.sort(key=lambda x: coordText[x]['coords'][0])
	cluster_y_list = list(map(lambda x: (0, coordText[x]['coords'][1]), cluster))
  
	y_cluster = AgglomerativeClustering(
    n_clusters=None,
    affinity='manhattan',
    linkage='complete',
    distance_threshold=20
  )

	y_cluster.fit(cluster_y_list)
	sorted_y_clusters = []
	for l in np.unique(y_cluster.labels_):
		idxs = np.where(y_cluster.labels_ == l)[0]
		sorted_y_clusters.append(idxs)
  
	sorted_y_clusters.sort(key=lambda x: x[0])
	sorted_y_clusters = list(itertools.chain.from_iterable(sorted_y_clusters))
  
	cluster = [cluster[x] for x in sorted_y_clusters]
  
  

	mini_cluster = {
      'text':'',
      'idx':(0, 0)
	}

	last_distance = 0
	for cluster_idx, idx in enumerate(cluster):
		(x, y, w, h) = coordText[idx]['coords']

		if last_distance == 0:
			mini_cluster['idx'] = (x, x + w)
			mini_cluster['text'] = coordText[idx]['text']
		elif abs(x - last_distance) < 15:
			mini_cluster['idx'] = (mini_cluster['idx'][0], x + w)
			mini_cluster['text'] += ' ' + coordText[idx]['text']
		elif abs(mini_cluster['idx'][0] - x) < 5:
			mini_cluster['idx'] = (mini_cluster['idx'][0], x + w)
			mini_cluster['text'] += ' ' + coordText[idx]['text']
		else:
			words.append(mini_cluster.copy())
			mini_cluster['idx'] = (x, x + w)
			mini_cluster['text'] = coordText[idx]['text']

		if cluster_idx == len(cluster) - 1:
			words.append(mini_cluster.copy())

		last_distance = x + w
	
	return words

@wrap
def cluster_coords(coordText, dist_thresh, thresh_change=0):
	"""
	Runs the clustering algorithm on the given coordinates
	Args:
		coordText (_type_): _description_
	"""
	yCoords = [(0, c['coords'][1]) for c in coordText]

	clustering = AgglomerativeClustering(
		n_clusters=None,
    	affinity='manhattan',
    	linkage='single',
    	distance_threshold=dist_thresh + thresh_change
	)

	clustering.fit(yCoords)

	sortedClusters =[]

	for l in np.unique(clustering.labels_):
		idxs = np.where(clustering.labels_ == l)[0]
  
		if len(idxs) > 1:
			sortedClusters.append(idxs)


	sortedClusters.sort(key=lambda x: x[0])

	wordClusters = list(map(lambda x: map_cluster(x, coordText), sortedClusters))

	for i in range(len(wordClusters)):
		wordClusters[i] = list(filter(lambda x: x['text'] != '$', wordClusters[i]))
  
	return wordClusters

@wrap
def find_clusters(wordClusters, img):
	clusters = []
	for words in wordClusters:
		min_cluster = []
		for dicts in words:
			x, y = abs(dicts['idx'][0] - img.shape[1]), abs(dicts['idx'][1] - img.shape[1])
			if (abs(x - dicts['idx'][1]) < 2 or abs(y - dicts['idx'][0]) < 2):
				continue
			if '_'  in dicts['text'] or '—' in dicts['text']:
				dicts['text'] = dicts['text'].replace('—', '-')
				dicts['text'] = dicts['text'].replace('_', '')
			min_cluster.append(dicts)
		if min_cluster:
			clusters.append(min_cluster)
	return clusters


@wrap
def find_targets(clusters, num_columns):
	targets = [[] for _ in range(num_columns)]

	for row in clusters[::-1]:
		if len(row) == num_columns:
			for i, val in enumerate(list(map(lambda x: x['idx'], row))):
				if i == 0:
					targets[i].append(val[0])
				else:
					targets[i].append(val[1])

	targets = [stats.mode(x)[0][0] for x in targets]

	return targets

@wrap
def create_dataframe_from_clusters(clusters, targets, num_columns):
	df = pd.DataFrame(columns=[i for i in range(num_columns)])

	for idx, row in enumerate(clusters):
		col = [''] * num_columns
		for val in row:
			mapped_targets = []
			for i in range(len(targets)):
				if i == 0:
					mapped_targets.append(abs(targets[i] - val['idx'][0]))
				else:
					mapped_targets.append(abs(targets[i] - val['idx'][1]))
			col_idx = np.argmin(mapped_targets)
			col[col_idx] = val['text']
  	
		df.loc[idx] = col


	return df