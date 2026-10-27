info = note_box(
  "Every method so far was <b>supervised</b>, learning from labelled examples. This chapter switches "
  "to <b>unsupervised</b> learning, which finds structure in <b>unlabelled</b> data where there are no "
  "correct answers to match. <b>k-means</b> groups points into <b><i>k</i></b> clusters by repeatedly "
  "assigning each point to the nearest centre and then moving each centre to the mean of its assigned "
  "points" + cite(6) + ". The data below has three natural groups.")

def render(k=3):
    # pure-numpy k-means (Lloyd's algorithm) with several restarts — keep the best
    # (lowest inertia); no scikit-learn, so it runs anywhere
    k = int(k)
    blobs = np.vstack([rng.normal(c, 0.45, (60, 2)) for c in ([0, 0], [3, 3], [0, 3])])
    def _one(seed):
        r = np.random.default_rng(seed)
        centers = blobs[r.choice(len(blobs), k, replace=False)].copy()
        labels = np.zeros(len(blobs), dtype=int)
        for _ in range(50):
            d = ((blobs[:, None, :] - centers[None, :, :])**2).sum(2)
            labels = d.argmin(1)
            newc = np.array([blobs[labels == j].mean(0) if np.any(labels == j) else centers[j]
                             for j in range(k)])
            if np.allclose(newc, centers):
                break
            centers = newc
        inertia = float(((blobs - centers[labels])**2).sum())
        return inertia, centers, labels
    inertia, centers, labels = min((_one(s) for s in range(10)), key=lambda t: t[0])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(blobs[:, 0], blobs[:, 1], c=labels, cmap="tab10", s=18)
    ax.scatter(centers[:, 0], centers[:, 1], c="black", marker="X", s=140)
    ax.set_title("k-means, k=%d (inertia %s)" % (k, fnum(inertia))); ax.grid(alpha=.3)
    return fig

viz = [viz_intro_box("",
        "The points carry no labels, yet k-means still groups them into <b><i>k</i></b> clusters on its "
        "own: colours show the discovered groups and the black crosses mark the cluster centres. The "
        "data has three natural groups, so set " + imath("k=3", color="#6b4a5e") + " to recover them, "
        "then try " + imath("k=2", color="#6b4a5e") + ", which is forced to merge two real groups, and " +
        imath("k=5", color="#6b4a5e") + ", which splits them apart, to see why the choice of "
        "<b><i>k</i></b> matters so much.")]
viz += slider_plot(render, {"k": IntSlider(value=3, min=2, max=6, step=1, description="k")})

interp = interpretation_box(
    "The colours show the discovered groups and the black crosses mark the cluster centres. With " +
    imath("k=3") + " the natural groups are recovered, while too small a <b><i>k</i></b> merges real "
    "groups and too large a <b><i>k</i></b> splits them. Choosing <b><i>k</i></b> is the hard part of "
    "clustering, so use the elbow or silhouette method rather than guesswork (verify the AI).")

build_chapter(8, "Unsupervised learning: Clustering", info=info, viz=viz, interp=interp)
