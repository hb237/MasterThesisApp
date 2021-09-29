from graphviz import Digraph
from pandas.core.frame import DataFrame
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.bpmn.util.sorting import get_sorted_nodes_edges
import tempfile


def apply(bpmn_graph, xes_log_tree, currency: str, currency_rate: float, ndigits=int(2), format="png", rankdir="LR", font_size=12):
    font_size = str(font_size)
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph(filename=filename.name, engine='dot', graph_attr={
                  'bgcolor': 'transparent'})
    viz.graph_attr['rankdir'] = rankdir

    nodes, edges = get_sorted_nodes_edges(bpmn_graph)

    events = xes_log_tree.findall(".//event")
    event_stats = []

    for e in events:
        task_name = str(e.find(".//string[@key='concept:name']").get('value'))
        cost_total = float(e.find(".//float[@key='cost:total']").get('value'))
        tx_number_of_events = int(
            e.find(".//int[@key='tx_number_of_events']").get('value'))
        avg_cost_event = cost_total / tx_number_of_events
        event_stats.append([task_name, avg_cost_event])

    df = DataFrame(event_stats, columns=['task_name', 'avg_cost_event'])
    df = df.groupby('task_name').mean()
    df = df.reset_index()
    df.rename(columns={'avg_cost_event': 'avg_avg_cost_event'}, inplace=True)
    task_stats = dict(zip(df['task_name'], df['avg_avg_cost_event']))
    for task in task_stats:
        task_stats[task] = round(task_stats[task] * currency_rate, ndigits)

    # for each event get tx_number_of_events
    # for each event get cost:total
    # for each event calc avg cost: cost:total tx_number_of_events
    # for each task calc avg of avg event cost

    for n in nodes:
        n_id = str(id(n))
        if isinstance(n, BPMN.Task):
            task_name = n.get_name()
            task_avg_cost = task_stats.get(task_name)
            label = '<<B>' + task_name + '</B><BR/>avg. cost: ' + \
                str(task_avg_cost) + ' ' + currency + '>'
            viz.node(n_id, shape="box", label=label, fontsize=font_size)
        elif isinstance(n, BPMN.StartEvent):
            viz.node(n_id, label="", shape="circle", style="filled",
                     fillcolor="green", fontsize=font_size)
        elif isinstance(n, BPMN.EndEvent):
            viz.node(n_id, label="", shape="circle", style="filled",
                     fillcolor="orange", fontsize=font_size)
        elif isinstance(n, BPMN.ParallelGateway):
            viz.node(n_id, label="+", shape="diamond",
                     fontsize=font_size)
        elif isinstance(n, BPMN.ExclusiveGateway):
            viz.node(n_id, label="X", shape="diamond",
                     fontsize=font_size)
        elif isinstance(n, BPMN.InclusiveGateway):
            viz.node(n_id, label="O", shape="diamond",
                     fontsize=font_size)
        elif isinstance(n, BPMN.OtherEvent):
            viz.node(n_id, label="", shape="circle", fontsize=font_size)

    for e in edges:
        n_id_1 = str(id(e[0]))
        n_id_2 = str(id(e[1]))

        viz.edge(n_id_1, n_id_2)

    viz.attr(overlap='false')

    viz.format = format

    return viz
