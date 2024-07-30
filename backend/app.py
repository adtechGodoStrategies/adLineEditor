from flask import Flask, request, jsonify
from flask_cors import CORS
import _locale
import re
from datetime import datetime
from googleads import ad_manager

_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load the Ad Manager client details from stored authorization.
ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()

# Connect to the Ad Manager network
network_service = ad_manager_client.GetService(
    'NetworkService', version='v202405')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    print('Received Data:', data)

    orden = data.get('orden')
    price = float(data.get('price', 12.0))
    limit = float(data.get('limit', 20.0))
    line_name_template = data.get('line_name_template')
    lineItemType = data.get('lineItemType')
    priority = data.get('priority')
    inventoryInclude = data.get('inventoryInclude', [])
    inventoryExclude = data.get('inventoryExclude', [])
    expectedCreative = data.get('expectedCreative')
    deliverySettings = data.get('deliverySettings')
    customTime = data.get('customTime')
    endSettings = data.get('endSettings')
    endDate = data.get('endDate')
    endTime = data.get('endTime')
    goalUnits = int(data.get('goalUnits', 100))
    creativeRotationType = data.get('creativeRotationType', 'EVEN')
    roadblockingType = data.get('roadblockingType', 'AS_MANY_AS_POSSIBLE')
    customTargeting = data.get('customTargeting', [])
    placement = data.get('placement')

    inventory_map = {
        'LV': '62332164',
        'MD': '57362484',
        'RAC1': '70115964'
    }

    exclude_map = {
        'comer': '66970884',
        'historiayvida': '21799279351',
        'magazine': '21960565090',
        'motor': '22069771456'
    }

    targetedAdUnits = [{'adUnitId': inventory_map[unit]}
                       for unit in inventoryInclude if unit in inventory_map]
    excludedAdUnits = [{'adUnitId': exclude_map[unit]}
                       for unit in inventoryExclude if unit in exclude_map]

    if not targetedAdUnits and not excludedAdUnits:
        return jsonify({'error': 'At least one inventory unit is required'}), 400

    if expectedCreative == '728x90':
        creative_placeholder_size = {'width': '728', 'height': '90'}
    elif expectedCreative == '1x1':
        creative_placeholder_size = {'width': '1', 'height': '1'}
    else:
        return jsonify({'error': 'Invalid creative size'}), 400

    if deliverySettings == 'IMMEDIATELY':
        startDateTimeType = 'IMMEDIATELY'
        startDateTime = None
    else:
        try:
            startDateTime = datetime.strptime(
                f"{deliverySettings} {customTime}", '%d/%m/%Y %H:%M')
            startDateTimeType = None
        except ValueError:
            return jsonify({'error': 'Invalid date or time format'}), 400

    if endSettings == 'UNLIMITED':
        unlimitedEndDateTime = True
        endDateTime = None
    else:
        unlimitedEndDateTime = False
        try:
            endDateTime = datetime.strptime(
                f"{endDate} {endTime}", '%d/%m/%Y %H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid end date or time format'}), 400

    filename = f"line_items_create_lines_lv_anot_{str(price)}_to_{
        str(limit)}.txt"
    with open(filename, "a") as f:
        updated_count = 0

        def select_Network():
            test_redes = network_service.getAllNetworks()
            for i, network in enumerate(test_redes):
                f.write(f"{i}. Network '{network['networkCode']}' '{
                        network['displayName']}'\n")
                f.write("\n")
            num_red = 0
            current_network = test_redes[num_red]
            ad_manager_client.network_code = current_network['networkCode']
            f.write(f"\nCurrent network: {
                    current_network['networkCode']} - {current_network['displayName']}\n")
            print(f"Current network: {
                  current_network['networkCode']} - {current_network['displayName']}")

        def select_and_print_orders(order_id):
            order_service = ad_manager_client.GetService(
                'OrderService', version='v202405')
            statement = (ad_manager.StatementBuilder().Where(
                'id = :id').WithBindVariable('id', int(order_id)).Limit(1))
            response = order_service.getOrdersByStatement(
                statement.ToStatement())

            if 'results' in response and len(response['results']):
                order = response['results'][0]
                f.write(f"\nWorking with Order {order_id} - {order['name']}\n")
                print(f"Working with Order {order_id} - {order['name']}")
            else:
                f.write(f"No order found with ID {order_id}")
                print(f"No order found with ID {order_id}")
                return None
            return order_id

        def select_and_print_lines(order_id):
            line_item_service = ad_manager_client.GetService(
                'LineItemService', version='v202405')
            statement = (ad_manager.StatementBuilder().Where(
                'orderId = :orderId').WithBindVariable('orderId', int(order_id)))
            response = line_item_service.getLineItemsByStatement(
                statement.ToStatement())
            line_items = getattr(response, 'results', [])
            f.write(f"Found {len(line_items)
                             } line items for Order {order_id}\n")
            print(f"Found {len(line_items)} line items for Order {order_id}")
            for line in line_items:
                f.write(f"Name: {line['name']}\nID: {line['id']}\n")
                print(f"Name: {line['name']}\nID: {line['id']}")
            return line_items

        def create_line_item(order_id, line_name, price, id_price):
            line_item_service = ad_manager_client.GetService(
                'LineItemService', version='v202405')
            line_item = {
                'name': line_name,
                'orderId': order_id,
                'startDateTimeType': startDateTimeType,
                'unlimitedEndDateTime': unlimitedEndDateTime,
                'creativeRotationType': creativeRotationType,
                'roadblockingType': roadblockingType,
                'childContentEligibility': 'ALLOWED',
                'allowOverbook': 'true',
                'skipInventoryCheck': 'true',
                'creativePlaceholders': [{'size': creative_placeholder_size, 'creativeSizeType': 'PIXEL'}],
                'lineItemType': lineItemType,
                'priority': priority,
                'deliveryRateType': 'EVENLY',
                'targeting': {
                    'geoTargeting': {
                        'targetedLocations': [{'id': '2724', 'displayName': 'SPAIN'}, {'id': '2484', 'displayName': 'MEXICO'}]
                    },
                    'inventoryTargeting': {
                        'targetedAdUnits': targetedAdUnits,
                        'excludedAdUnits': excludedAdUnits
                    },
                    'customTargeting': {
                        'xsi_type': 'CustomCriteriaSet',
                        'logicalOperator': 'OR',
                        'children': [
                            {
                                'xsi_type': 'CustomCriteriaSet',
                                'logicalOperator': 'AND',
                                'children': [
                                    {'xsi_type': 'CustomCriteria', 'keyId': 147444,
                                        'operator': 'IS', 'valueIds': customTargeting},
                                    {'xsi_type': 'CustomCriteria', 'keyId': 147684,
                                        'operator': 'IS', 'valueIds': [placement]},
                                    {'xsi_type': 'CustomCriteria', 'keyId': 217884,
                                        'operator': 'IS', 'valueIds': [id_price]}
                                ]
                            }
                        ]
                    }
                },
                'costType': 'CPM',
                'costPerUnit': {'currencyCode': 'EUR', 'microAmount': "{:.0f}".format(price * 1000000)},
                'primaryGoal': {
                    'goalType': 'DAILY',
                    'units': goalUnits
                }
            }

            if not targetedAdUnits and not excludedAdUnits:
                return jsonify({'error': 'At least one inventory unit is required'}), 400

            if startDateTime:
                line_item['startDateTime'] = {
                    'date': {
                        'year': startDateTime.year,
                        'month': startDateTime.month,
                        'day': startDateTime.day
                    },
                    'hour': startDateTime.hour,
                    'minute': startDateTime.minute,
                    'second': 0,
                    'timeZoneId': 'Europe/Madrid'
                }

            if endDateTime:
                line_item['endDateTime'] = {
                    'date': {
                        'year': endDateTime.year,
                        'month': endDateTime.month,
                        'day': endDateTime.day
                    },
                    'hour': endDateTime.hour,
                    'minute': endDateTime.minute,
                    'second': 0,
                    'timeZoneId': 'Europe/Madrid'
                }

            created_line_item = line_item_service.createLineItems([line_item])[
                0]
            f.write(f"New Line Item created with ID {
                    created_line_item['id']} and name {created_line_item['name']}\n")
            print(f"New Line Item created with ID {
                  created_line_item['id']} and name {created_line_item['name']}")
            return created_line_item['id'], created_line_item['name']

        def create_creative(order_id, width, height):
            creative_service = ad_manager_client.GetService(
                'CreativeService', version='v202405')
            creative = {
                'xsi_type': 'TemplateCreative',
                'name': f'Creative Rich Audience Header bidding',
                'advertiserId': get_advertiser_id(order_id),
                'size': {'width': width, 'height': height},
                'creativeTemplateId': 12262965,
            }
            created_creative = creative_service.createCreatives([creative])[0]
            f.write(f"New Creative created with ID {
                    created_creative['id']} and name {created_creative['name']}\n")
            print(f"New Creative created with ID {
                  created_creative['id']} and name {created_creative['name']}")
            return created_creative['id']

        def association_line_with_creative(created_line_item, created_creative):
            line_item_creative_association_service = ad_manager_client.GetService(
                'LineItemCreativeAssociationService', version='v202405')
            creative_association = {
                'creativeId': created_creative, 'lineItemId': created_line_item}
            line_item_creative_association_service.createLineItemCreativeAssociations([
                                                                                      creative_association])
            f.write(f"Creative assigned to Line Item with ID {
                    created_creative}\n")
            print(f"Creative assigned to Line Item with ID {created_creative}")

        def get_advertiser_id(order_id):
            statement = (ad_manager.StatementBuilder().Where(
                'orderId = :orderId').WithBindVariable('orderId', int(order_id)))
            order_service = ad_manager_client.GetService(
                'OrderService', version='v202405')
            responseOrder = order_service.getOrdersByStatement(
                statement.ToStatement())
            order = responseOrder['results'][0]
            advertiser_id = order['advertiserId']
            return advertiser_id

        def get_all_hb_pb(price):
            target_name_value = price
            custom_targeting_service = ad_manager_client.GetService(
                'CustomTargetingService', version='v202405')
            value_statement = (ad_manager.StatementBuilder().Where(
                'customTargetingKeyId = :keyId').WithBindVariable('keyId', int(217884)))
            value_statement.Offset(0).Limit(500)
            values_response = custom_targeting_service.getCustomTargetingValuesByStatement(
                value_statement.ToStatement())
            while True:
                if 'results' in values_response:
                    for value in values_response['results']:
                        targeting_value_id = value['id']
                        targeting_value_name = value['name']
                        if str(targeting_value_name).strip() == str(target_name_value).strip():
                            return targeting_value_id
                    value_statement.Offset(value_statement.offset + 100)
                    values_response = custom_targeting_service.getCustomTargetingValuesByStatement(
                        value_statement.ToStatement())
                else:
                    break

        select_Network()
        order_id = select_and_print_orders(orden)
        if not order_id:
            return jsonify({'error': 'Order not found'}), 404

        line_items = select_and_print_lines(order_id)
        while price <= limit:
            id_price = get_all_hb_pb("{:.2f}".format(price))
            line_name = f"{line_name_template} {price}"

            line_item_id, line_item_name = create_line_item(
                order_id, line_name, price, id_price)
            creative_id = create_creative(
                order_id, creative_placeholder_size['width'], creative_placeholder_size['height'])
            association_line_with_creative(line_item_id, creative_id)
            price = round(price + 0.50, 2)
            updated_count += 1

        f.write(f"Total line items updated: {updated_count}\n")
        print(f"Total line items updated: {updated_count}")
        return jsonify({'resultado': f"Líneas creadas correctamente. Total line items updated: {updated_count}"})


if __name__ == '__main__':
    app.run(debug=True)
