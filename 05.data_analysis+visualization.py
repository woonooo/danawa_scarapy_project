# 군집분석 1

# 화장대의 사이즈 가로와 세로를 이용한 kmeans (scale, elbow 하지않고 임의로 해봄)    
# 데이터 = 화장대와 붙박이장만 추린 1271개의 데이터
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

data1 = danawa_final_all_data.iloc[:,[22,23]]

model = KMeans(n_clusters=5, algorithm='auto')
model.fit(data1)
predict = pd.DataFrame(model.predict(data1))
predict.columns = ['predict']

result_data1 = pd.concat([data1,predict],axis=1)

plt.figure(figsize=(10,6))
for i in np.unique(predict):
    plt.scatter(result_data1.loc[result_data1['predict']==i, 'size_har'], result_data1.loc[result_data1['predict']==i, 'size_ver'], label = i, alpha=0.7)
plt.xlabel("Horizontal")
plt.ylabel("Vertical")
plt.legend()
plt.show()




# 군집분석 2

# PCA4, kmeans 군집9 실시(이전에 수많은 과정을 거쳐서 9번째 군집실시하는 코드)   
# 데이터: 최소한의 데이터만 제거(size와 6month_price, price 세개의 결측치 제거)한 1905개
# 표준화 실시
test_data = danawa_drop_data.copy()

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
data_scale = scaler.fit_transform(test_data)
data_scale = pd.DataFrame(data_scale, columns = test_data.columns)
data_scale.head(2)

# PCA실행
from sklearn.decomposition import PCA

pca = PCA(random_state=1222)
x_p = pca.fit_transform(data_scale)
pd.Series(np.cumsum(pca.explained_variance_ratio_))

pca_data = pd.DataFrame(x_p)
pca_comp3_data = pca_data.iloc[:,[0,1,2]]
pca_comp3_data.info()

# elbow graph
from sklearn.cluster import KMeans
elbow = []
k = range(1,10)
for i in k:
    model = KMeans(n_clusters=i)
    model.fit(pca_comp3_data)
    elbow.append(model.inertia_)

plt.plot(k, elbow, 'bx-')
plt.xlabel('k')
plt.show()

# Kmeans 실시
model = KMeans(n_clusters=3)

model.fit(pca_comp3_data)
predict = pd.DataFrame(model.predict(pca_comp3_data))
predict.columns = ['predict']
result_data2 = pd.concat([pca_comp3_data, predict], axis = 1)

# Kmeans 결과 그래프
plt.figure(figsize=(10,6))
for i in np.unique(predict):
    plt.scatter(result_data2.loc[result_data2['predict']==i, 0], result_data2.loc[result_data2['predict']==i, 1], label = i)
plt.legend()
plt.show()

# 각 예측값의 개수와 최솟값을 출력
for i in np.unique(predict):
    temp_data = test_data['min_price'].loc[result_data2.loc[result_data2['predict']==i].index]
    print(i, ':', np.mean(temp_data))

predict.value_counts()




# 군집결과 확인용 데이터
check_data = danawa_data3.drop(danawa_data2.iloc[:, [0,1,5,6,9,10,11,12,13,14,15,16,18, 21]].columns, axis=1)
check_data.info()

# 군집 데이터 확인 -> 고가의 제품제외 후 다시 군집해보자!
check_data.loc[result_data2.loc[result_data2['predict'] == 2].index]
check_data[check_data['made_by']=='베이직가구']

# 이상치 제거
# 이상치를 제거하고 다시 군집실시해볼것   
result_data2.loc[result_data2['predict'] == 1].index
danawa_no_outlier_data = danawa_final_all_data.loc[danawa_final_data.index.isin(result_data2.loc[result_data2['predict'] == 0].index.append(result_data2.loc[result_data2['predict'] == 1].index))]
danawa_no_outlier_data.reset_index(inplace=True, drop=True)




# 군집분석 3

# 이상치 8개 제거하고 pca실행
# PCA5, kmeans 군집10 실시   
# 데이터: 최소한의 데이터만 제거(size와 6month_price, price 세개의 결측치 제거)한 1905개 -> 이상치 8개 제거 == 1897개

test_data = danawa_no_outlier_data.drop(danawa_no_outlier_data.iloc[:, [0,1,2,3,4,5,6,9,10,11,12,13,14,15,16,18,21]].columns, axis=1)
test_data.info()

made_by = dict(zip(list(test_data.iloc[:,0].unique()), 
                   list(range(len(test_data.iloc[:,0].unique())))))

test_data['made_by'] = [made_by.get(i) for i in test_data['made_by']]
test_data.info()

# 표준화
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
data_scale = scaler.fit_transform(test_data)
data_scale = pd.DataFrame(data_scale, columns = test_data.columns)
data_scale.head(2)

# PCA실행
from sklearn.decomposition import PCA

pca = PCA(random_state=1222)
x_p = pca.fit_transform(data_scale)
pd.Series(np.cumsum(pca.explained_variance_ratio_))

pca_data2 = pd.DataFrame(x_p)
pca.explained_variance_

comp = pd.DataFrame(pca.components_.T)
comp.index = data_scale.columns

pca_comp3_data = pca_data2.iloc[:,[0,1,2]]
pca_comp3_data.info()

# elbow graph
from sklearn.cluster import KMeans

elbow = []
k = range(1,10)
for i in k:
    model = KMeans(n_clusters=i)
    model.fit(pca_comp3_data)
    elbow.append(model.inertia_)

plt.plot(k, elbow, 'bx-')
plt.xlabel('k')
plt.show()

# Kmeans 실시
model = KMeans(n_clusters=3)

model.fit(pca_comp3_data)
predict = pd.DataFrame(model.predict(pca_comp3_data))
predict.columns = ['predict']
result_data2 = pd.concat([pca_comp3_data, predict], axis = 1)

# Kmeans 결과 그래프
plt.figure(figsize=(10,6))
for i in np.unique(predict):
    plt.scatter(result_data2.loc[result_data2['predict']==i, 0], result_data2.loc[result_data2['predict']==i, 1], label = i)
plt.legend()
plt.show()

# 각 예측값의 개수와 최솟값을 출력
for i in np.unique(predict):
    temp_data = test_data['min_price'].loc[result_data2.loc[result_data2['predict']==i].index]
    print(i, ':', np.mean(temp_data))

predict.value_counts()

# 3d graph
fig = plt.figure(figsize = (15,15))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(result_data2.loc[result_data2['predict']==0,0],result_data2.loc[result_data2['predict']==0,1],result_data2.loc[result_data2['predict']==0,2], s = 40 , color = 'blue', label = "cluster 0")
ax.scatter(result_data2.loc[result_data2['predict']==1,0],result_data2.loc[result_data2['predict']==1,1],result_data2.loc[result_data2['predict']==1,2], s = 40 , color = 'orange', label = "cluster 1")
ax.scatter(result_data2.loc[result_data2['predict']==2,0],result_data2.loc[result_data2['predict']==2,1],result_data2.loc[result_data2['predict']==2,2], s = 40 , color = 'green', label = "cluster 2")
ax.set_xlabel('component0-->')
ax.set_ylabel('component1-->')
ax.set_zlabel('component2-->')
ax.legend()
plt.show()
'''
component 0: size_har, min_price, info_all의 영향으로 복합적   
component 1: size_ver과 info_all,int_closet의 음의 영향   
component 2: price_slope, regisger_date의 영향   
'''



# 군집분석 4

# DBSCAN을 이용한 군집분석
# pca를 진행후, 3개의 요인으로 구성된 데이터
pca_comp3_data.info()

from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=3, min_samples=5)
dbscan.fit(pca_comp3_data)

dbscan.labels_[:10]
len(dbscan.core_sample_indices_)
dbscan.components_[:3]

def plot_dbscan(dbscan, X, size, show_xlabels=True, show_ylabels=True):
    core_mask = np.zeros_like(dbscan.labels_, dtype=bool)
    core_mask[dbscan.core_sample_indices_] = True
    anomalies_mask = dbscan.labels_ == -1
    non_core_mask = ~(core_mask | anomalies_mask)

    cores = dbscan.components_
    anomalies = X[anomalies_mask]
    non_cores = X[non_core_mask]
    
    plt.scatter(cores[:, 0], cores[:, 1],
                c=dbscan.labels_[core_mask], marker='o', s=size, cmap="Paired")
    plt.scatter(cores[:, 0], cores[:, 1], marker='*', s=20, c=dbscan.labels_[core_mask])
    plt.scatter(anomalies[:, 0], anomalies[:, 1],
                c="r", marker="x", s=30)
    plt.scatter(non_cores[:, 0], non_cores[:, 1], c=dbscan.labels_[non_core_mask], marker=".")
    if show_xlabels:
        plt.xlabel("$x_1$", fontsize=14)
    else:
        plt.tick_params(labelbottom=False)
    if show_ylabels:
        plt.ylabel("$x_2$", fontsize=14, rotation=0)
    else:
        plt.tick_params(labelleft=False)
    plt.title("eps={:.2f}, min_samples={}".format(dbscan.eps, dbscan.min_samples), fontsize=14)

plt.figure(figsize=(20, 9))
plt.subplot(121)
plot_dbscan(dbscan, np.array(pca_comp3_data.iloc[:,[0,1]]), size=100)
plt.show()




# 군집분석 5

# 차원을 축소하는 방법을 pca가 아닌 시각화를 위한 차원축소 방법 t-SNE을 이용한 후, DBSCAN을 이용한 군집분석
# 사용하는 데이터는 표준화가 실시된 데이터를 이용
from sklearn.manifold import TSNE

tsne = TSNE(n_components=2, random_state=42)
X_reduced_tsne = tsne.fit_transform(data_scale)

# 다시 dbscan 적용
dbscan = DBSCAN(eps=3.5, min_samples=7)
dbscan.fit(X_reduced_tsne)

dbscan.labels_[:10]
len(dbscan.core_sample_indices_)
dbscan.components_[:3]

def plot_dbscan(dbscan, X, size, show_xlabels=True, show_ylabels=True):
    core_mask = np.zeros_like(dbscan.labels_, dtype=bool)
    core_mask[dbscan.core_sample_indices_] = True
    anomalies_mask = dbscan.labels_ == -1
    non_core_mask = ~(core_mask | anomalies_mask)

    cores = dbscan.components_
    anomalies = X[anomalies_mask]
    non_cores = X[non_core_mask]
    
    plt.scatter(cores[:, 0], cores[:, 1],
                c=dbscan.labels_[core_mask], marker='o', s=size, cmap="Paired")
    plt.scatter(cores[:, 0], cores[:, 1], marker='*', s=20, c=dbscan.labels_[core_mask])
    plt.scatter(anomalies[:, 0], anomalies[:, 1],
                c="r", marker="x", s=30)
    plt.scatter(non_cores[:, 0], non_cores[:, 1], c=dbscan.labels_[non_core_mask], marker=".")
    if show_xlabels:
        plt.xlabel("$x_1$", fontsize=14)
    else:
        plt.tick_params(labelbottom=False)
    if show_ylabels:
        plt.ylabel("$x_2$", fontsize=14, rotation=0)
    else:
        plt.tick_params(labelleft=False)
    plt.title("eps={:.2f}, min_samples={}".format(dbscan.eps, dbscan.min_samples), fontsize=14)


plt.figure(figsize=(20, 9))
plt.subplot(121)
plot_dbscan(dbscan, np.array(pca_comp3_data.iloc[:,[0,1]]), size=100)
plt.show()

dbscan.labels_.shape

# 각 예측값의 개수와 최솟값을 출력
for i in set(dbscan.labels_):
    price = np.mean(test_data[dbscan.labels_==i].min_price)
    print(i, ': ', round(price), "원", len(test_data[dbscan.labels_==i]), "개")




'''
이외 병합군집과 LDA를 실행해보았지만 이도 모두 만족스럽지 않은 결과가 나타남

# 병합군집을 했을 때, 클러스터의 수가 2개로 나옴ㅜ
from sklearn.cluster import AgglomerativeClustering
X = data_scale
agg = AgglomerativeClustering(linkage="complete").fit(X)
agg.n_clusters_

# LDA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

lda = LinearDiscriminantAnalysis(n_components=2)
X_mnist = mnist["data"]
y_mnist = mnist["target"]
lda.fit(X_mnist, y_mnist)
X_reduced_lda = lda.transform(X_mnist)
'''




