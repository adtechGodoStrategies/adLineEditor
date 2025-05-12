import time
from datetime import datetime
from googleads import ad_manager
from zeep.helpers import serialize_object  # Asegúrate de importar esto

RETRY_LIMIT = 3
RETRY_DELAY = 5  # seconds

# Load the Ad Manager client details from stored authorization.
ad_manager_client = ad_manager.AdManagerClient.LoadFromStorage()
network_service = ad_manager_client.GetService(
    'NetworkService', version='v202405')


def update_lines(data):
    orden = data.get('orden')
    min_cpm = float(data.get('minCPM', 4.0))  # Valor por defecto 4€, pero puede cambiar
    hbDeal = data.get('hbDeal', [])
    hbDealNone = data.get('hbDealNone', [])
    hbDealRemove = data.get('hbDealRemove', [])
    hbDealNoneRemove = data.get('hbDealNoneRemove', [])
    lineItemType = data.get('lineItemType')  # New field to update lineItemType
    priority = data.get('priority')  # New field to update priority
    # Recogemos el tamaño de la creatividad que el usuario introduce.
    expectedCreative = data.get('expectedCreative')

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
        
        def select_and_print_lines(order_id, min_cpm):
            """
            Obtiene y filtra las líneas de pedido de un orden específico,
            asegurando que solo se consideren aquellas con un CPM mayor o igual al valor especificado.

            :param order_id: ID de la orden en Google Ad Manager.
            :param min_cpm: CPM mínimo en euros que deben cumplir las líneas.
            :return: Lista de líneas de pedido que cumplen con el filtro.
            """
            line_item_service = ad_manager_client.GetService('LineItemService', version='v202405')

            # Consultar las líneas de pedido de la orden
            statement = (ad_manager.StatementBuilder()
                        .Where('orderId = :orderId')
                        .WithBindVariable('orderId', int(order_id)))
            response = line_item_service.getLineItemsByStatement(statement.ToStatement())

            # Obtener las líneas de pedido
            line_items = getattr(response, 'results', [])
            filtered_lines = []  # Lista de líneas que cumplen con el filtro de CPM

            print(f"🔍 Buscando líneas de pedido en la orden {order_id} con CPM mínimo de {min_cpm}€...")

            for line in line_items:
                cpm_micro_amount = line['costPerUnit']['microAmount']
                cpm_euros = cpm_micro_amount / 1_000_000  # Convertimos microAmount a euros

                if cpm_euros >= min_cpm:
                    filtered_lines.append(line)  # Agregamos solo las líneas que cumplen con el CPM mínimo
                    print(f"✅ Line Item {line['id']} ({line['name']}) tiene CPM {cpm_euros}€ (SE actualizará).")
                else:
                    print(f"❌ Line Item {line['id']} ({line['name']}) tiene CPM {cpm_euros}€ (NO se actualizará).")

            print(f"🔹 Total líneas seleccionadas para actualización: {len(filtered_lines)}")
            return filtered_lines  # Solo devolvemos las líneas con CPM ≥ min_cpm

        def update_line_item(line_item):
    

            line_item_service = ad_manager_client.GetService('LineItemService', version='v202405')

            # Verifica si la línea está archivada antes de continuar
            if 'isArchived' in line_item and line_item['isArchived']:
                print(f"❌ Line Item {line_item['id']} está archivado, saltando actualización.")
                return False

            line_item['allowOverbook'] = True
            line_item['skipInventoryCheck'] = True

            # Actualiza el tipo de línea y la prioridad si se proporcionan
            if lineItemType:
                line_item['lineItemType'] = lineItemType
            if priority:
                line_item['priority'] = int(priority)

            if 'primaryGoal' not in line_item or line_item['primaryGoal'] is None:
                line_item['primaryGoal'] = {'goalType': 'DAILY', 'units': 100}
            else:
                try:
                    line_item['primaryGoal']['goalType'] = 'DAILY'
                    line_item['primaryGoal']['units'] = 100
                except AttributeError:
                    setattr(line_item['primaryGoal'], 'goalType', 'DAILY')
                    setattr(line_item['primaryGoal'], 'units', 100)

                    
            # Actualiza los tamaños de creatividad solo si se proporcionan
            if expectedCreative and len(expectedCreative) > 0:
                if 'creativePlaceholders' not in line_item:
                    line_item['creativePlaceholders'] = []

                valid_creatives = []
                for creative in expectedCreative:
                    if 'x' in creative:
                        width, height = creative.split('x')
                        new_creative = {
                            'size': {'width': int(width), 'height': int(height)},
                            'creativeSizeType': 'PIXEL'
                        }
                        valid_creatives.append(new_creative)
                    else:
                        print(f"⚠️ Formato de tamaño de creatividad inválido: {creative}")

                if valid_creatives:
                    line_item['creativePlaceholders'] = valid_creatives
                else:
                    print(f"⚠️ No se encontraron creatividades válidas para Line Item {line_item['id']}, omitiendo actualización de creatividades.")

            # Si la segmentación personalizada existe y se proporciona hbDeal o hbDealNone
            if ('hbDeal' in data and len(hbDeal) > 0) or ('hbDealNone' in data and len(hbDealNone) > 0):
                if 'targeting' in line_item and 'customTargeting' in line_item['targeting']:
                    custom_targeting = line_item['targeting']['customTargeting']

                    hbDeal_found = False
                    hbDealNone_found = False
                    for criteria_set in custom_targeting['children']:
                        for criterion in criteria_set['children']:
                            if criterion['keyId'] == 11921921:
                                if criterion['operator'] == 'IS':
                                    existing_hbDeal_values = set(criterion['valueIds'])
                                    updated_hbDeal_values = existing_hbDeal_values.union(set(int(value) for value in hbDeal))
                                    updated_hbDeal_values.difference_update(set(int(value) for value in hbDealRemove))
                                    criterion['valueIds'] = list(updated_hbDeal_values)
                                    hbDeal_found = True
                                elif criterion['operator'] == 'IS_NOT':
                                    existing_hbDealNone_values = set(criterion['valueIds'])
                                    updated_hbDealNone_values = existing_hbDealNone_values.union(set(int(value) for value in hbDealNone))
                                    updated_hbDealNone_values.difference_update(set(int(value) for value in hbDealNoneRemove))
                                    criterion['valueIds'] = list(updated_hbDealNone_values)
                                    hbDealNone_found = True

                    if not hbDeal_found and len(hbDeal) > 0:
                        new_custom_criteria = {
                            'xsi_type': 'CustomCriteria',
                            'keyId': 11921921,
                            'operator': 'IS',
                            'valueIds': [int(value) for value in hbDeal]
                        }
                        custom_targeting['children'].append(new_custom_criteria)

                    if not hbDealNone_found and len(hbDealNone) > 0:
                        new_custom_criteria_not = {
                            'xsi_type': 'CustomCriteria',
                            'keyId': 11921921,
                            'operator': 'IS_NOT',
                            'valueIds': [int(value) for value in hbDealNone]
                        }
                        custom_targeting['children'].append(new_custom_criteria_not)
                        
            # **** Nueva lógica para actualizar el campo "start time" ****
            # Si la línea aún no ha iniciado (la fecha de inicio es futura), se actualiza para que inicie inmediatamente.
            import datetime
            import pytz  # Asegúrate de tener pytz instalado

            madrid_tz = pytz.timezone('Europe/Madrid')

            if 'startDateTime' in line_item:
                scheduled = line_item['startDateTime']
               # print(f"DEBUG: startDateTime raw value: {scheduled}")
               # print(f"DEBUG: Type of scheduled: {type(scheduled)}")

                if isinstance(scheduled, dict):
                   # print("DEBUG: scheduled is dict")
                    try:
                       # print(f"DEBUG: scheduled dict keys: {list(scheduled.keys())}")
                        naive_dt = datetime.datetime(
                            scheduled['date']['year'],
                            scheduled['date']['month'],
                            scheduled['date']['day'],
                            scheduled.get('hour', 0),
                            scheduled.get('minute', 0),
                            scheduled.get('second', 0)
                        )
                       # print(f"DEBUG: Naive datetime constructed from dict: {naive_dt}")
                        scheduled_datetime = madrid_tz.localize(naive_dt)
                       # print(f"DEBUG: Timezone aware datetime from dict: {scheduled_datetime}")
                    except Exception as e:
                        #print(f"⚠️ ERROR parsing dict startDateTime for line {line_item['id']}: {e}")
                        scheduled_datetime = None
                elif isinstance(scheduled, datetime.datetime):
                   # print("DEBUG: scheduled is datetime object")
                    if scheduled.tzinfo is None:
                        #print("DEBUG: scheduled is naive datetime, localizing...")
                        scheduled_datetime = madrid_tz.localize(scheduled)
                    else:
                        #print("DEBUG: scheduled is timezone aware datetime")
                        scheduled_datetime = scheduled
                    #print(f"DEBUG: scheduled_datetime: {scheduled_datetime}")
                elif isinstance(scheduled, str):
                    #print("DEBUG: scheduled is string")
                    try:
                        naive_dt = datetime.datetime.strptime(scheduled, "%d/%m/%Y")
                        #print(f"DEBUG: Naive datetime from string: {naive_dt}")
                        scheduled_datetime = madrid_tz.localize(naive_dt)
                        #print(f"DEBUG: Timezone aware datetime from string: {scheduled_datetime}")
                    except Exception as e:
                        #print(f"⚠️ ERROR parsing string startDateTime for line {line_item['id']}: {e}")
                        scheduled_datetime = None
                # Nueva rama para objetos zeep: comprobamos por el nombre de la clase.

                elif scheduled.__class__.__name__ == 'DateTime':
                    #print("DEBUG: scheduled is a zeep DateTime object, converting to dict")
                    try:
                        scheduled_dict = serialize_object(scheduled)
                        #print(f"DEBUG: Converted zeep DateTime to dict: {scheduled_dict}")
                        naive_dt = datetime.datetime(
                            scheduled_dict['date']['year'],
                            scheduled_dict['date']['month'],
                            scheduled_dict['date']['day'],
                            scheduled_dict.get('hour', 0),
                            scheduled_dict.get('minute', 0),
                            scheduled_dict.get('second', 0)
                        )
                        #print(f"DEBUG: Naive datetime constructed from zeep dict: {naive_dt}")
                        scheduled_datetime = madrid_tz.localize(naive_dt)
                        #print(f"DEBUG: Timezone aware datetime from zeep object: {scheduled_datetime}")
                    except Exception as e:
                        #print(f"⚠️ ERROR parsing zeep DateTime for line {line_item['id']}: {e}")
                        scheduled_datetime = None
                else:
                    #print("DEBUG: scheduled is of unknown type")
                    scheduled_datetime = None

                now_madrid = datetime.datetime.now(madrid_tz)
                #print(f"DEBUG: now_madrid: {now_madrid}")
                #print(f"DEBUG: scheduled_datetime final: {scheduled_datetime}")

                if scheduled_datetime and scheduled_datetime > now_madrid:
                    line_item['startDateTimeType'] = 'IMMEDIATELY'
                    #print(f"DEBUG: Updating start time to IMMEDIATELY for line {line_item['id']}")
                else:
                    print(f"DEBUG: Not updating start time for line {line_item['id']}, condition not met")
            else:
                line_item['startDateTimeType'] = 'IMMEDIATELY'
                #print(f"DEBUG: startDateTime not present, setting to IMMEDIATELY for line {line_item['id']}")



            # **** Fin de la lógica para start time ****

            # **** Lógica para actualizar el "end time" a UNLIMITED ****
            # Inserta estas dos líneas aquí, justo después de la lógica de start time y antes de llamar a la API:
            line_item['unlimitedEndDateTime'] = True
            line_item['endDateTime'] = None
            print(f"🔄 Se actualiza end time de la línea {line_item['id']} a UNLIMITED (unlimitedEndDateTime = True).")
        # **** Fin de la lógica para end time ****
            for attempt in range(RETRY_LIMIT):
                try:
                    updated_line_item = line_item_service.updateLineItems(
                        [line_item], {'skipInventoryCheck': True, 'allowOverbook': True})
                    line_name = line_item['name']
                    print(f"✅ Line Item actualizado: {updated_line_item[0]['id']} - Nombre: {line_name}")
                    return True
                except Exception as e:
                    error_message = f"❌ Error actualizando Line Item {line_item['id']} - Intento {attempt + 1}: {str(e)}"
                    print(error_message)

                    # Escribir el error en el archivo de registro
                    f.write(f"{error_message}\n")


                    # Si el error es de "DURATION_NOT_ALLOWED", lo notificamos pero seguimos con la siguiente línea
                    if "ReservationDetailsError.DURATION_NOT_ALLOWED" in error_message:
                        print(f"⚠️ Error con la duración en línea {line_item['id']} - Se omite la actualización y se continúa con la siguiente línea.")
                        return False  # Saltar a la siguiente línea sin detener el script

                    # Si el error es CONCURRENT_MODIFICATION, reintentar
                    if 'CONCURRENT_MODIFICATION' in str(e) and attempt < RETRY_LIMIT - 1:
                        print(f"🔄 Error de modificación concurrente, intento {attempt + 1}/{RETRY_LIMIT}. Reintentando en {RETRY_DELAY} segundos...")
                        time.sleep(RETRY_DELAY)
                    else:
                        print(f"⚠️ Se omite la actualización de Line Item {line_item['id']} y se continúa con la siguiente línea.")
                        return False  # Continúa con la siguiente línea sin detener el programa

            return False  # Si después de varios intentos no se actualiza, continuar con la siguiente línea


        select_Network()
        order_id = select_and_print_orders(orden)
        if not order_id:
            raise ValueError('Order not found')

        line_items = select_and_print_lines(order_id,min_cpm)
        for line_item in line_items:
            if update_line_item(line_item):
                updated_count += 1

        f.write(f"Total line items updated: {updated_count}\n")
        print(f"Total line items updated: {updated_count}")
        return f"Líneas actualizadas correctamente. Total line items updated: {updated_count}"
