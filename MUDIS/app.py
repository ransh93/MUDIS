import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from logic.mudgee_parser import Parser
from logic.comparison import MudComparer
from logic.mongo_dal import MongoDal
import logic.constants as constants
from logic.mud_generalization import MudGeneralization
import uuid
from flask import g
from statistics import mean
from muddy.models import Protocol

app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER
app.secret_key = 'super secret key'
mongo_dal = MongoDal('MudRun', 'muds')


@app.route('/addmud')
def add_mud():
    return render_template('addmud.html')

@app.route('/')
@app.route('/mudscoordinator')
def mudscoordinator():

    columns = [
        {
            "field": 'state',
            "checkbox": True,
            "align": 'center',
        },
        {
            "field": "mud_name",
            "title": "mud_name",
            "sortable": True,
        },
        {
            "field": "device_type",
            "title": "device type",
            "sortable": True,
        },
        {
            "field": "device_name",
            "title": "device_name",
            "sortable": True,
        },
        {
            "field": "dev_location",
            "title": "device location",
            "sortable": True,
            "align": 'center',
            "clickToSelect": False,
            "formatter": "countryFormatter"
        },
        {
            "field": 'operate',
            "title": 'Mud Operate',
            "align": 'center',
            "clickToSelect": False,
            "events": "window.operateEvents",
            "formatter": "operateFormatter"
        }
    ]

    muds_data = mongo_dal.read_all()
    data = prepare_mud_data(muds_data)
    return render_template("mudscoordinator.html", data=data, columns=columns)

@app.route('/getMudContent', methods = ['GET', 'POST'])
def present_mud_content():
    mud_id = request.args.get('mud_id')
    condition = { "_id" : '{0}'.format(mud_id) }
    mud_data = mongo_dal.read(condition)
    mud_content = mud_data["mud_content"]

    return mud_content


def prepare_mud_data(muds_data):
    documents_length = muds_data.count()
    data = {"total": documents_length,
            "totalNotFiltered": documents_length,
            "rows": []
           }

    for mud_document in muds_data:
        filtered_dict = {k: v for k, v in mud_document.items() if k in constants.DATA_TO_COLUMNS}
        data["rows"].append(filtered_dict)

    return data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in constants.ALLOWED_EXTENSIONS


@app.route('/uploadMud', methods = ['GET', 'POST'])
def upload_mud():
    # check if the post request has the file part
    if 'mud_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    mud_file = request.files.get('mud_file')

    if mud_file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if mud_file and allowed_file(mud_file.filename):
        mud_content = mud_file.read()
        mud_filename = secure_filename(mud_file.filename)
        mud_file_path = os.path.join(app.config['UPLOAD_FOLDER'], mud_filename)
        mud_file.stream.seek(0)
        mud_file.save(mud_file_path)
    else:
        return "Wrong file format"

    data = request.form.to_dict()
    data['mud_file_path'] = mud_file_path
    data['mud_content'] = mud_content
    data['_id'] = str(uuid.uuid4())

    # insert the given data in to the DB
    mongo_dal.insert(data)

    # redirect to the main page of the app
    return redirect(url_for('mudscoordinator'))


@app.route('/generalized_mud', methods=['GET', 'POST'])
def get_generalized_mud():
    if g.mud_genaralization is None:
        generalized_mud_rules = g.mud_genaralization.from_rules + g.mud_genaralization.to_rules
        return render_template('show_generalized_mud.html', generalized_mud_rules=generalized_mud_rules)
    else:
        return render_template('show_generalized_mud.html', generalized_mud_rules=None)

@app.route('/list_compare', methods=['GET', 'POST'])
def list_compare_muds():
    list_of_muds_to_compare = [("no_vpn_blink-camera_merged_ukMud.json", "vpn_blink-camera_merged_ukMud.json", "blink-camera_uk"),
                               ("no_vpn_blink-camera_merged_usMud.json", "vpn_blink-camera_merged_usMud.json", "blink-camera_us"),

                               ("no_vpn_yi-camera_merged_ukMud.json", "vpn_yi-camera_merged_ukMud.json", "yi-camera_uk"),
                               ("no_vpn_yi-camera_merged_usMud.json", "vpn_yi-camera_merged_usMud.json", "yi-camera_us"),

                               ("no_vpn_xiaomi-hub_merged_ukMud.json", "vpn_xiaomi-hub_merged_ukMud.json", "xiaomi-hub_uk"),
                               ("no_vpn_xiaomi-hub_merged_usMud.json", "vpn_xiaomi-hub_merged_usMud.json", "xiaomi-hub_us"),

                               ("no_vpn_xiaomi-cleaner_merged_ukMud.json", "vpn_xiaomi-cleaner_merged_ukMud.json", "xiaomi-cleaner_uk"),
                               ("no_vpn_xiaomi-cleaner_merged_usMud.json", "vpn_xiaomi-cleaner_merged_usMud.json", "xiaomi-cleaner_us"),

                               ("no_vpn_wansview-cam-wired_merged_ukMud.json", "vpn_wansview-cam-wired_merged_ukMud.json", "wansview-cam-wired_uk"),
                               ("no_vpn_wansview-cam-wired_merged_usMud.json", "vpn_wansview-cam-wired_merged_usMud.json", "wansview-cam-wired_us"),

                               ("no_vpn_t-wemo-plug_merged_ukMud.json", "vpn_t-wemo-plug_merged_ukMud.json", "t-wemo-plug_uk"),
                               ("no_vpn_t-wemo-plug_merged_usMud.json", "vpn_t-wemo-plug_merged_usMud.json", "t-wemo-plug_us"),

                               ("no_vpn_tplink-plug_merged_ukMud.json", "vpn_tplink-plug_merged_ukMud.json", "tplink-plug_uk"),
                               ("no_vpn_tplink-plug_merged_usMud.json", "vpn_tplink-plug_merged_usMud.json", "tplink-plug_us"),

                               ("no_vpn_tplink-bulb_merged_ukMud.json", "vpn_tplink-bulb_merged_ukMud.json", "tplink-bulb_uk"),
                               ("no_vpn_tplink-bulb_merged_usMud.json", "vpn_tplink-bulb_merged_usMud.json", "tplink-bulb_us"),

                               ("no_vpn_t-philips-hub_merged_ukMud.json", "vpn_t-philips-hub_merged_ukMud.json", "t-philips-hub_uk"),
                               ("no_vpn_t-philips-hub_merged_usMud.json", "vpn_t-philips-hub_merged_usMud.json", "t-philips-hub_us"),

                               ("no_vpn_sousvide_merged_ukMud.json", "vpn_sousvide_merged_ukMud.json", "sousvide_uk"),
                               ("no_vpn_sousvide_merged_usMud.json", "vpn_sousvide_merged_usMud.json", "sousvide_us"),

                               ("no_vpn_smartthings-hub_merged_ukMud.json", "vpn_smartthings-hub_merged_ukMud.json", "smartthings-hub_uk"),
                               ("no_vpn_smartthings-hub_merged_usMud.json", "vpn_smartthings-hub_merged_usMud.json", "smartthings-hub_us"),

                               ("no_vpn_sengled-hub_merged_ukMud.json", "vpn_sengled-hub_merged_ukMud.json", "sengled-hub_uk"),
                               ("no_vpn_sengled-hub_merged_usMud.json", "vpn_sengled-hub_merged_usMud.json", "sengled-hub_us"),

                               ("no_vpn_samsungtv-wired_merged_ukMud.json", "vpn_samsungtv-wired_merged_ukMud.json", "samsungtv-wired_uk"),
                               ("no_vpn_samsungtv-wired_merged_usMud.json", "vpn_samsungtv-wired_merged_usMud.json", "samsungtv-wired_us"),

                               ("no_vpn_roku-tv_merged_ukMud.json", "vpn_roku-tv_merged_ukMud.json", "roku-tv_uk"),
                               ("no_vpn_roku-tv_merged_usMud.json", "vpn_roku-tv_merged_usMud.json", "roku-tv_us"),

                               ("no_vpn_ring-doorbell_merged_ukMud.json", "vpn_ring-doorbell_merged_ukMud.json", "ring-doorbell_uk"),
                               ("no_vpn_ring-doorbell_merged_usMud.json", "vpn_ring-doorbell_merged_usMud.json", "ring-doorbell_us"),

                               ("no_vpn_nest-tstat_merged_ukMud.json", "vpn_nest-tstat_merged_ukMud.json", "nest-tstat_uk"),
                               ("no_vpn_nest-tstat_merged_usMud.json", "vpn_nest-tstat_merged_usMud.json", "nest-tstat_us"),

                               ("no_vpn_magichome-strip_merged_ukMud.json", "vpn_magichome-strip_merged_ukMud.json", "magichome-strip_uk"),
                               ("no_vpn_magichome-strip_merged_usMud.json", "vpn_magichome-strip_merged_usMud.json", "magichome-strip_us"),

                               ("no_vpn_lightify-hub_merged_ukMud.json", "vpn_lightify-hub_merged_ukMud.json", "lightify-hub_uk"),
                               ("no_vpn_lightify-hub_merged_usMud.json", "vpn_lightify-hub_merged_usMud.json", "lightify-hub_us"),

                               ("no_vpn_insteon-hub_merged_ukMud.json", "vpn_insteon-hub_merged_ukMud.json", "insteon-hub_uk"),
                               ("no_vpn_insteon-hub_merged_usMud.json", "vpn_insteon-hub_merged_usMud.json", "insteon-hub_us"),

                               ("no_vpn_google-home-mini_merged_ukMud.json", "vpn_google-home-mini_merged_ukMud.json", "google-home-mini_uk"),
                               ("no_vpn_google-home-mini_merged_usMud.json", "vpn_google-home-mini_merged_usMud.json", "google-home-mini_us"),

                               ("no_vpn_firetv_merged_ukMud.json", "vpn_firetv_merged_ukMud.json", "firetv_uk"),
                               ("no_vpn_firetv_merged_usMud.json", "vpn_firetv_merged_usMud.json", "firetv_us"),

                               ("no_vpn_echospot_merged_ukMud.json", "vpn_echospot_merged_ukMud.json", "echospot_uk"),
                               ("no_vpn_echospot_merged_usMud.json", "vpn_echospot_merged_usMud.json", "echospot_us"),

                               ("no_vpn_echoplus_merged_ukMud.json", "vpn_echoplus_merged_ukMud.json", "echoplus_uk"),
                               ("no_vpn_echoplus_merged_usMud.json", "vpn_echoplus_merged_usMud.json", "echoplus_us"),

                               ("no_vpn_echodot_merged_ukMud.json", "vpn_echodot_merged_ukMud.json", "echodot_uk"),
                               ("no_vpn_echodot_merged_usMud.json", "vpn_echodot_merged_usMud.json", "echodot_us"),

                               ("no_vpn_blink-security-hub_merged_ukMud.json", "vpn_blink-security-hub_merged_ukMud.json", "blink-security-hub_uk"),
                               ("no_vpn_blink-security-hub_merged_usMud.json", "vpn_blink-security-hub_merged_usMud.json", "blink-security-hub_us"),

                               ("no_vpn_appletv_merged_ukMud.json", "vpn_appletv_merged_ukMud.json", "appletv_uk"),
                               ("no_vpn_appletv_merged_usMud.json", "vpn_appletv_merged_usMud.json", "appletv_us")]

    list_of_regular_muds_to_compare = [
        ("blink_camera_merged_ukMud.json", "blink_camera_merged_usMud.json", "blink_camera"),
        ("yi_camera_merged_ukMud.json", "yi_camera_merged_usMud.json", "yi_camera"),
        ("xiaomi_hub_merged_ukMud.json", "xiaomi_hub_merged_usMud.json", "xiaomi_hub"),
        ("xiaomi_cleaner_merged_ukMud.json", "xiaomi_cleaner_merged_usMud.json", "xiaomi_cleaner"),
        ("wansview_cam_merged_ukMud.json", "wansview_cam_merged_usMud.json", "wansview_cam_wired"),
        ("t_wemo_plug_merged_ukMud.json", "t_wemo_plug_merged_usMud.json", "t_wemo_plug"),
        ("tplink_plug_merged_ukMud.json", "tplink_plug_merged_usMud.json", "tplink_plug"),
        ("tplink_bulb_merged_ukMud.json", "tplink_bulb_merged_usMud.json", "tplink_bulb"),
        ("t_philips_hub_merged_ukMud.json", "t_philips_hub_merged_usMud.json", "t_philips_hub"),
        ("sousvide_merged_ukMud.json", "sousvide_merged_usMud.json", "sousvide"),
        ("smartthings_hub_merged_ukMud.json", "smartthings_hub_merged_usMud.json", "smartthings_hub"),
        ("sengled_hub_merged_ukMud.json", "sengled_hub_merged_usMud.json", "sengled_hub"),
        ("samsungtv_wired_merged_ukMud.json", "samsungtv_wired_merged_usMud.json", "samsungtv_wired"),
        ("roku_tv_merged_ukMud.json", "roku_tv_merged_usMud.json", "roku_tv"),
        ("ring_doorbell_merged_ukMud.json", "ring_doorbell_merged_usMud.json", "ring_doorbell"),
        ("nest_tstat_merged_ukMud.json", "nest_tstat_merged_usMud.json", "nest_tstat"),
        ("magichome_strip_merged_ukMud.json", "magichome_strip_merged_usMud.json", "magichome_strip"),
        ("lightify_hub_merged_ukMud.json", "lightify_hub_merged_usMud.json", "lightify_hub"),
        ("insteon_hub_merged_ukMud.json", "insteon_hub_merged_usMud.json", "insteon_hub"),
        ("google_home_mini_merged_ukMud.json", "google_home_mini_merged_usMud.json", "google_home_mini"),
        ("fire_tv_merged_ukMud.json", "fire_tv_merged_usMud.json", "firetv"),
        ("echo_spot_merged_ukMud.json", "echo_spot_merged_usMud.json", "echospot"),
        ("echo_plus_merged_ukMud.json", "echo_plus_merged_usMud.json", "echoplus"),
        ("echo_dot_merged_ukMud.json", "echo_dot_merged_usMud.json", "echodot"),
        ("blink_security_hub_merged_ukMud.json", "blink_security_hub_merged_usMud.json", "blink_security_hub"),
        ("no_vpn_appletv_merged_ukMud.json", "no_vpn_appletv_merged_usMud.json", "appletv"),
        ]

    similarity_scores = []
    similarity_scores_avg = []

    #list_of_muds_to_compare
    #list_of_regular_muds_to_compare

    for compare_tuple in list_of_muds_to_compare:
        first_mud = compare_tuple[0]
        second_mud = compare_tuple[1]
        device_name = compare_tuple[2]

        compare_object = parse_muds_and_compare(first_mud, second_mud, False)
        similarity_score = compare_object[1][0]
        similarity_score = '{:.4f}'.format(similarity_score)
        similarity_scores.append((device_name, similarity_score, len(compare_object[2])))
        similarity_scores_avg.append(float(similarity_score))


    number_of_comparisions_above_09 = list(filter(lambda score: score >= 0.9, similarity_scores_avg))
    number_of_comparisions_above_08_lower_to_09 = list(filter(lambda score: 0.9 > score >= 0.8, similarity_scores_avg))
    number_of_comparisions_lower_08 = list(filter(lambda score: 0.8 > score, similarity_scores_avg))

    print(len(similarity_scores))
    print(similarity_scores)
    similarity_scores_avg.sort()
    print(similarity_scores_avg)
    print(mean(similarity_scores_avg))


    return render_template('list_compare.html', similarity_scores=similarity_scores, number_of_comparisions_above_09=number_of_comparisions_above_09,
    number_of_comparisions_above_08_lower_to_09=number_of_comparisions_above_08_lower_to_09, number_of_comparisions_lower_08=number_of_comparisions_lower_08)



@app.route('/compare', methods=['GET', 'POST'])
def compare_muds():
    first_mud_path = request.form.get('first_mud_path')
    second_mud_path = request.form.get('second_mud_path')
    first_mud_name = request.form.get('first_mud_name')
    second_mud_name = request.form.get('second_mud_name')
    first_mud_location = request.form.get('first_mud_location')
    second_mud_location = request.form.get('second_mud_location')
    device_type = request.form.get('device_type')
    device_name = request.form.get('device_name')
    dns_filter = request.form.get('dns_filter')
    ntp_filter = request.form.get('ntp_filter')
    p2p_filter = request.form.get('p2p_filter')
    inner_ip_filter = request.form.get('inner_ip_filter')

    compare_object = parse_muds_and_compare(first_mud_path, second_mud_path, False, dns_filter, ntp_filter, p2p_filter, inner_ip_filter)
    two_directional_dt = compare_object[0]
    compare_metrices = compare_object[1]
    identical_rules = compare_object[2]
    non_similar_rules = compare_object[3]
    similar_rules = compare_object[4]
    related_rules = compare_object[5]
    relations_graph = compare_object[6]
    domain_similar_rules = compare_object[7]
    not_domain_similar_rules = compare_object[8]
    non_similar_rules_for_presentation = (non_similar_rules[0], non_similar_rules[2])

    mud_genaralization = MudGeneralization(identical_rules, non_similar_rules[0], non_similar_rules[1],
                         non_similar_rules[2], non_similar_rules[3], similar_rules[0], similar_rules[1],
                         first_mud_name, first_mud_location, second_mud_name, second_mud_location, device_type, device_name, mongo_dal)

    generalized_mud_rules = mud_genaralization.from_rules + mud_genaralization.to_rules

    head, first_file_name = os.path.split(first_mud_path)
    head, second_file_name = os.path.split(second_mud_path)

    return render_template('comparison.html', generalized_mud_rules=generalized_mud_rules, identical_rules=identical_rules, domain_similar_rules=domain_similar_rules,
                           not_domain_similar_rules=not_domain_similar_rules,
                           non_similar_rules_for_presentation=non_similar_rules_for_presentation , first_direction_dt=two_directional_dt[0],
                           second_direction_dt=two_directional_dt[1], first_mud_filename=first_file_name,
                           second_mud_filename=second_file_name, compare_metrices=compare_metrices,related_rules=related_rules,
                           nodes=relations_graph[0], edges=relations_graph[1],
                           first_mud_location=first_mud_location, second_mud_location=second_mud_location)


def parse_muds_and_compare(first_mud_file, second_mud_file, full_path=True, dns_filter=0, ntp_filter=0, p2p_filter=0, inner_ip_filter=0):

    if full_path:
        first_mud_file_path = first_mud_file
        second_mud_file_path = second_mud_file
    else:
        first_mud_file_path = os.path.join(constants.UPLOAD_FOLDER, first_mud_file)
        second_mud_file_path = os.path.join(constants.UPLOAD_FOLDER, second_mud_file)

    # first mud
    first_mud_parser = Parser(first_mud_file_path)
    first_mud_parser.parse_metadata()
    first_mud_parser.parse_access_lists()

    # second mud
    second_mud_parser = Parser(second_mud_file_path)
    second_mud_parser.parse_metadata()
    second_mud_parser.parse_access_lists()

    # compare muds
    mud_comparer = MudComparer(first_mud_parser.mud, second_mud_parser.mud)
    # 9998-9999 Ring Socket Service of ring-doorbell - https://support.ring.com/hc/en-us/articles/205385394-The-Protocols-and-Ports-Used-by-Ring-Devices
    # 10000-65535 for all other amazone devices

    if dns_filter == '1':
        dns_filter = True
        icmp_filter = True
    else:
        dns_filter = False
        icmp_filter = False

    if ntp_filter == '1':
        ntp_filter = True
    else:
        ntp_filter = False

    if p2p_filter == '1':
        p2p_filter = True
        port_range = [(10000,65535, Protocol.UDP), (9998,9999, Protocol.TCP)]
    else:
        p2p_filter = False
        port_range = None

    if inner_ip_filter == '1':
        inner_ip_filter = True
    else:
        inner_ip_filter = False

    mud_comparer.clean_mud_out_of_noise(dns_filter, icmp_filter, ntp_filter, inner_ip_filter, port_range)

    mud_comparer.compare_muds()
    nodes, ages = mud_comparer.create_relations_graph()

    # calculates compare metrices
    first_metric = mud_comparer.odd_rules_out_of_total_rules()
    second_metric = mud_comparer.odd_rules_without_similar_rules_out_of_total_rules()
    third_metric = mud_comparer.generalization_rating()

    metrices = (first_metric, second_metric, third_metric)
    identical_rules = mud_comparer.final_identical_dt
    related_rules = (mud_comparer.first_from_related_aces, mud_comparer.first_to_related_aces)
    non_similar_rules = (mud_comparer.non_similar_first_from_aces, mud_comparer.non_similar_first_to_aces,
                         mud_comparer.non_similar_second_from_aces, mud_comparer.non_similar_second_to_aces)
    similar_rules = (mud_comparer.similar_first_from_related_aces, mud_comparer.similar_first_to_related_aces)
    domain_similar_rules = (mud_comparer.domain_based_similar_first_from_related_aces, mud_comparer.domain_based_similar_first_to_related_aces)
    not_domain_similar_rules = (mud_comparer.not_domain_based_similar_first_from_related_aces, mud_comparer.not_domain_based_similar_first_to_related_aces)
    graph = (nodes, ages)

    return mud_comparer.two_directional_comparison, metrices, identical_rules, non_similar_rules, \
           similar_rules, related_rules, graph,\
           mud_comparer.prepare_similarity_rules_for_presentation(domain_similar_rules), \
           mud_comparer.prepare_similarity_rules_for_presentation(not_domain_similar_rules), \
           mud_comparer.prepare_non_similarity_rules_for_presentation((non_similar_rules[0], non_similar_rules[2]))


if __name__ == '__main__':
    app.run()
