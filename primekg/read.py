import pandas as pd
import ipdb
import networkx

primekg = pd.read_csv('kg.csv', low_memory=False)
print(primekg.head(), primekg.tail())
ipdb.set_trace()

def extrac_subgrap(kg):
    # extract subgraphs based on the network motifs 
    # all the three node motifs and the popular network motifs (feedforward-loop, Bi-fan, fully connected triad, uplinked mutual dyad)according to https://www.science.org/doi/10.1126/science.298.5594.824
    # 
    # also extract the 13 types of three node subgraphs based on network motifs
    # after extraction, save the subgraphs in seperate files
    primekg.drop_duplicates(subset=["x_id", "y_id"])
    ipdb.set_trace()
    
    sub1= get_sub1()
    # feed-forward loop
    ffd = get_feedforward()
    # bi-fan
    biFan = get_bi_fan()


    return
def get_sub1():
    out = list()
    #first fan
    for row_1 in primekg.itertuples(name="Pandas"):
        row_2 = primekg[primekg["x_id"].isin([row_1.x_id])&~primekg["y_id"].isin([row_1.y_id])]
        if not row_2.empty:
            out.append((row_1.x_id, row_1.y_id), (row_2.x_id, row_2.y_id))
    return out

def get_sub2():
    out = list()
    for row_1 in primekg.itertuples(name="Pandas"):
        for row_2 in primekg.itertuples(name="Pandas"):
            if row_1.y_id == row_2.x_id:
                if row_1.x_id != row_2.y_id:
                    out.append([(row_1.x_id, row_1.y_id), (row_2.x_id, row_2.y_id), (row_1.x_id, row_2.y_id)])
    return out

def get_sub3():
    out = list()
    for row_1 in primekg.itertuples(name="Pandas"):
        for row_2 in primekg.itertuples(name="Pandas"):
            if row_1.y_id == row_2.x_id:
                if row_1.x_id != row_2.y_id:
                    out.append([(row_1.x_id, row_1.y_id), (row_2.x_id, row_2.y_id), (row_1.x_id, row_2.y_id)])
    return out

def get_feedforward(primekg):
    out = list()
    for row_1 in primekg.itertuples(name="Pandas"):
        for row_2 in primekg.itertuples(name="Pandas"):
            if row_1.y_id == row_2.x_id:
                if row_1.x_id != row_2.y_id:
                    if not primekg[primekg["x_id"].isin([row_1.x_id]) & primekg["y_id"].isin([row_2.y_id])].empty:
                        out.append([(row_1.x_id, row_1.y_id), (row_2.x_id, row_2.y_id), (row_1.x_id, row_2.y_id)])
    return out

def get_bi_fan(primekg):
    out = list()
    #first fan
    for row_1 in primekg.itertuples(name="Pandas"):
        row_2 = primekg[primekg["x_id"].isin([row_1.x_id])&~primekg["y_id"].isin([row_1.y_id])]
        if not row_2.empty:
            # second fan
            row_3 = primekg[primekg["y_id"].isin([row_1.y_id]) & primekg["x_id"].isin([row_1.x_id])]
            if not row_3.empty:
                row_4 = primekg[primekg["y_id"].isin([row_2.y_id]) & primekg["x_id"].isin([row_1.x_id])]
                if not row_4.empty:
                    out.append([(row_1.x_id, row_1.y_id), (row_2.x_id, row_2.y_id), (row_3.x_id, row_3.y_id), (row_4.x_id, row_4.y_id)])
    return out


extrac_subgrap(primekg)