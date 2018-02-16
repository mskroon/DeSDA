import levenshtein
import senlen_ratio
import zhang_shasha_UD
import senvec
import networkx_GED
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.preprocessing import label_binarize



data = 'en-nl.syn.train'
udM1 = 'udpipe-ud-2.0-conll17-170315/models/english-ud-2.0-conll17-170315.udpipe' #a UDPipe model
udM2 = 'udpipe-ud-2.0-conll17-170315/models/dutch-ud-2.0-conll17-170315.udpipe' #a UDPipe model
train_dict = 'en-nl.basicwordlist.csv'
svM1 = 'model1.bin' #a fastText model for English (files too big to be on GitHub)
svM2 = 'model2.bin' #a fastText model for Dutch


methods = [
    ('lev', levenshtein.Levenshtein(data, removestopwords=False)),
    ('lev_rm', levenshtein.Levenshtein(data, removestopwords=True)),
    ('senlen', senlen_ratio.Senlen_ratio(data, removestopwords=False)),
    ('senlen_rm', senlen_ratio.Senlen_ratio(data, removestopwords=True)),
    ('ud', zhang_shasha_UD.Zhang_Shasha_UD(data, udM1, udM2, ignore_morphology=False, removestopwords=False)),
    ('ud_im', zhang_shasha_UD.Zhang_Shasha_UD(data, udM1, udM2, ignore_morphology=True, removestopwords=False)),
    ('ud_rm', zhang_shasha_UD.Zhang_Shasha_UD(data, udM1, udM2, ignore_morphology=False, removestopwords=True)),
    ('ud_rm_im', zhang_shasha_UD.Zhang_Shasha_UD(data, udM1, udM2, ignore_morphology=True, removestopwords=True)),
    ('nx_ged', networkx_GED.Networkx_GED(data, udM1, udM2)),
    ('nx_ged_tfidf', networkx_GED.Networkx_GED(data, udM1, udM2, tfidf=True)),
    ('nx_ged_im', networkx_GED.Networkx_GED(data, udM1, udM2, ignore_morphology=True)),
    ('nx_ged_im_tfidf', networkx_GED.Networkx_GED(data, udM1, udM2, ignore_morphology=True, tfidf=True)),
    ('nx_ged_rm', networkx_GED.Networkx_GED(data, udM1, udM2, removestopwords=True)),
    ('nx_ged_rm_tfidf', networkx_GED.Networkx_GED(data, udM1, udM2, removestopwords=True, tfidf=True)),
    ('nx_ged_im_rm', networkx_GED.Networkx_GED(data, udM1, udM2, ignore_morphology=True, removestopwords=True)),
    ('nx_ged_im_rm_tfidf', networkx_GED.Networkx_GED(data, udM1, udM2, ignore_morphology=True, removestopwords=True, tfidf=True)),
    ('nx_ged_man', networkx_GED.Networkx_GED(data, udM1, udM2, morphology_as_nodes=True)),
    ('nx_ged_man_tfidf', networkx_GED.Networkx_GED(data, udM1, udM2, morphology_as_nodes=True, tfidf=True)),
    ('nx_ged_rm_man', networkx_GED.Networkx_GED(data, udM1, udM2, removestopwords=True, morphology_as_nodes=True)),
    ('nx_ged_rm_man_tfidf', networkx_GED.Networkx_GED(data, udM1, udM2, removestopwords=True, morphology_as_nodes=True, tfidf=True)),
    ('sv', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=False, tfidf=False)),
    ('senvec_tf', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=False, tfidf=True)),
    ('senvec_rm', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=True, tfidf=False)),
    ('senvec_tf_rm', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=True, tfidf=True)),
    ('sv_g', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=False, tfidf=False, geometric=True)),
    ('senvec_tf_g', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=False, tfidf=True, geometric=True)),
    ('senvec_rm_g', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=True, tfidf=False, geometric=True)),
    ('senvec_tf_rm_g', senvec.Sen_vec_cossim(data, train_dict, svM1, svM2, removestopwords=True, tfidf=True, geometric=True))
]

# for method, label in zip(methods, labels):
results = []
for label, method in methods:
    print(label)
    # print(method)
    auc_above = roc_auc_score(label_binarize([p[1] for p in method], classes=['N', 'Y']), [p[0] for p in method])
    auc_below = roc_auc_score(label_binarize([p[1] for p in method], classes=['Y', 'N']), [p[0] for p in method])
    if auc_above > auc_below:
        roc = roc_curve(label_binarize([p[1] for p in method], classes=['N', 'Y']), [p[0] for p in method])
        label += '>'
        auc = auc_above
    else:
        roc = roc_curve(label_binarize([p[1] for p in method], classes=['Y', 'N']), [p[0] for p in method])
        label += '<'
        auc = auc_below
    # for x in zip(roc[0], roc[1]):
        # print(x, end='')
    # print()
    plt.plot(roc[0], roc[1], '-', label=label)
    roc = list(zip(*roc))
    print('AUC:', auc)
    results.append((label, auc))
    print('Youden:', max(roc, key=lambda x: x[1]-x[0]))
    print('Euclidean:', min(roc, key=lambda x: ((x[0]**2 + (1-x[1]**2))**.5)))
    print()
for m in sorted(results, key=lambda x:x[1]):
    print(m)

plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.axis([0, 1, 0, 1])
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
