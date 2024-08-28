import time
from datetime import datetime
from googleads import ad_manager

RETRY_LIMIT = 3
RETRY_DELAY = 5  # seconds

# Load the Ad Manager client details from stored authorization.
ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
network_service = ad_manager_client.GetService(
    'NetworkService', version='v202405')


def update_lines(data):
    orden = data.get('orden')
    hbDeal = data.get('hbDeal', [])
    hbDealNone = data.get('hbDealNone', [])
    hbDealRemove = data.get('hbDealRemove', [])
    hbDealNoneRemove = data.get('hbDealNoneRemove', [])

    filename = f"line_items_update_lines_{orden}_{
        datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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

        def update_line_item(line_item):
            line_item_service = ad_manager_client.GetService(
                'LineItemService', version='v202405')
            line_item['allowOverbook'] = True
            line_item['skipInventoryCheck'] = True

            if 'targeting' in line_item and 'customTargeting' in line_item['targeting']:
                custom_targeting = line_item['targeting']['customTargeting']

                # Buscar y actualizar el criterio de 'hbDeal'
                hbDeal_found = False
                hbDealNone_found = False
                for criteria_set in custom_targeting.children:
                    for criterion in criteria_set.children:
                        if criterion.keyId == 11921921:
                            if criterion.operator == 'IS':
                                existing_hbDeal_values = set(
                                    criterion.valueIds)
                                updated_hbDeal_values = existing_hbDeal_values.union(
                                    set(int(value) for value in hbDeal))
                                updated_hbDeal_values.difference_update(
                                    set(int(value) for value in hbDealRemove))
                                criterion.valueIds = list(
                                    updated_hbDeal_values)
                                hbDeal_found = True
                            elif criterion.operator == 'IS_NOT':
                                existing_hbDealNone_values = set(
                                    criterion.valueIds)
                                updated_hbDealNone_values = existing_hbDealNone_values.union(
                                    set(int(value) for value in hbDealNone))
                                updated_hbDealNone_values.difference_update(
                                    set(int(value) for value in hbDealNoneRemove))
                                criterion.valueIds = list(
                                    updated_hbDealNone_values)
                                hbDealNone_found = True

                if not hbDeal_found:
                    new_custom_criteria = {
                        'xsi_type': 'CustomCriteria',
                        'keyId': 11921921,
                        'operator': 'IS',
                        'valueIds': [int(value) for value in hbDeal]
                    }
                    custom_targeting.children.append(new_custom_criteria)

                if not hbDealNone_found:
                    new_custom_criteria_not = {
                        'xsi_type': 'CustomCriteria',
                        'keyId': 11921921,
                        'operator': 'IS_NOT',
                        'valueIds': [int(value) for value in hbDealNone]
                    }
                    custom_targeting.children.append(new_custom_criteria_not)

                for attempt in range(RETRY_LIMIT):
                    try:
                        updated_line_item = line_item_service.updateLineItems(
                            [line_item], {'skipInventoryCheck': True, 'allowOverbook': True})
                        line_name = line_item['name']
                        print(f"Updated Line Item: {
                              updated_line_item[0]['id']} - Name: {line_name}")
                        f.write(f"\nUpdated Line Item: {
                                updated_line_item[0]['id']} - Name: {line_name}\n")
                        return True
                    except Exception as e:
                        if 'CONCURRENT_MODIFICATION' in str(e) and attempt < RETRY_LIMIT - 1:
                            print(f"Concurrent modification error, attempt {
                                  attempt + 1}/{RETRY_LIMIT}. Retrying in {RETRY_DELAY} seconds...")
                            time.sleep(RETRY_DELAY)
                        else:
                            raise

            return False

        select_Network()
        order_id = select_and_print_orders(orden)
        if not order_id:
            raise ValueError('Order not found')

        line_items = select_and_print_lines(order_id)
        for line_item in line_items:
            if update_line_item(line_item):
                updated_count += 1

        f.write(f"Total line items updated: {updated_count}\n")
        print(f"Total line items updated: {updated_count}")
        return f"Líneas actualizadas correctamente. Total line items updated: {updated_count}"
