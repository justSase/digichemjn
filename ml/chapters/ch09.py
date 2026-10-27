_intro_txt = (
  "Placing a sigmoid on a line added a single non-linearity. A <b>neuron</b> generalises that idea: "
  "it takes a weighted sum of its inputs and passes it through an activation function. Stacking many "
  "such neurons into layers gives a <b>neural network</b> that can bend to fit almost any pattern, "
  "which is the foundation of modern deep learning" + cite(2, 4) + ".")

info = concept_box(_intro_txt, r"$a = f\!\left(w_1 x_1 + w_2 x_2 + \dots + w_n x_n + b\right)$",
    variables=[("a", "the neuron's output (activation)"),
               ("f", "non-linear activation function"),
               ("w&#7522;, x&#7522;", "weights and inputs"), ("b", "bias")],
    function="Without the non-linearity <b><i>f</i></b>, stacked layers collapse into a single line.")

def render_act(activation="relu"):
    z = np.linspace(-4, 4, 200)
    f = {"relu": np.maximum(0, z), "sigmoid": sigmoid(z), "tanh": np.tanh(z)}[activation]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(z, f, color="#2c6e91", lw=2.5); ax.axhline(0, color="gray", lw=.6); ax.axvline(0, color="gray", lw=.6)
    ax.set_title("activation: %s" % activation); ax.grid(alpha=.3)
    ax.set_xlabel("input z"); ax.set_ylabel("f(z)")
    return fig

def render_net(hidden_units=8, learning_rate=0.03):
    Xn = np.linspace(-3, 3, 120).reshape(-1, 1); yn = np.sin(Xn); r = np.random.default_rng(1)
    hu = int(hidden_units)
    W1 = r.normal(0, 0.8, (1, hu)); b1 = np.zeros((1, hu)); W2 = r.normal(0, 0.8, (hu, 1)); b2 = np.zeros((1, 1))
    for _ in range(3000):
        a1 = np.tanh(Xn@W1 + b1); d = (a1@W2 + b2 - yn)/len(Xn)
        gW2 = a1.T@d; gb2 = d.sum(0, keepdims=True); da1 = (d@W2.T)*(1 - a1**2)
        gW1 = Xn.T@da1; gb1 = da1.sum(0, keepdims=True)
        W1 -= learning_rate*gW1; b1 -= learning_rate*gb1; W2 -= learning_rate*gW2; b2 -= learning_rate*gb2
    yp = np.tanh(Xn@W1 + b1)@W2 + b2
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(Xn, yn, s=12, color="#9bb7c9", label="target sin(x)")
    ax.plot(Xn, yp, color="#b5482e", lw=2.5, label="%d units" % hu)
    ax.legend(); ax.grid(alpha=.3); ax.set_title("tiny neural net, MSE %s" % fnum(mse(yn, yp)))
    return fig

viz = [viz_intro_box("",
        "The activation is the small non-linearity inside each neuron, and it is what lets a network "
        "bend instead of staying a straight line. The dropdown draws the three most common choices so "
        "you can compare their shapes: <b>ReLU</b> passes positive inputs through unchanged and clips "
        "everything below zero, while <b>sigmoid</b> and <b>tanh</b> are smooth S-curves that flatten "
        "out for large positive or negative inputs. Switch between them and note where each one is flat "
        "and where it responds most strongly.")]
viz += slider_plot(render_act, {"activation": Dropdown(options=["relu", "sigmoid", "tanh"], value="relu", description="activation")})
viz += [viz_intro_box("",
        "Here a network with a single hidden layer, written in plain numpy, is trained to reproduce a "
        "curved target function (a sine wave). The number of hidden units sets the network's capacity "
        "and the learning rate sets the training step size. Start with " + imath("1", color="#6b4a5e") +
        " hidden unit, where the fit is almost a straight line with too little capacity to bend, then "
        "raise it toward " + imath("8", color="#6b4a5e") + " and " + imath("30", color="#6b4a5e") +
        " units and watch the curve follow the target ever more closely as capacity grows.")]
viz += slider_plot(render_net, {
    "hidden_units": IntSlider(value=8, min=1, max=30, step=1, description="units"),
    "learning_rate": FloatSlider(value=0.03, min=0.005, max=0.2, step=0.005, readout_format=".3f", description="lr")})

interp = interpretation_box(
    "Each activation bends the signal differently: <b>ReLU</b> zeroes negatives (simple, fast, the "
    "deep-learning default" + cite(4) + "), while <b>sigmoid/tanh</b> saturate smoothly. Stacking many such bent units is "
    "what gives a network its power to fit curves. With <b>1 unit</b> the tiny network is nearly a line, with too "
    "little capacity to bend; adding units lets it follow the sine ever more closely (MSE ↓). This is exactly "
    "how deep networks gain their expressive power: they combine many simple bent units.")

build_chapter(7, "Neural networks: Neurons, activations & a tiny network",
              info=info, viz=viz, interp=interp)
