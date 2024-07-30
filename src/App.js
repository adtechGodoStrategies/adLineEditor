import React, { useState } from 'react';
import './App.css';

function App() {
  const [orden, setOrden] = useState('');
  const [price, setPrice] = useState(12.0);
  const [limit, setLimit] = useState(20.0);
  const [lineNameTemplate, setLineNameTemplate] = useState('');
  const [lineItemType, setLineItemType] = useState('');
  const [priority, setPriority] = useState('');
  const [inventoryInclude, setInventoryInclude] = useState([]);
  const [inventoryExclude, setInventoryExclude] = useState([]);
  const [expectedCreative, setExpectedCreative] = useState('');
  const [deliverySettings, setDeliverySettings] = useState('IMMEDIATELY');
  const [customDate, setCustomDate] = useState('');
  const [customTime, setCustomTime] = useState('00:00');
  const [endSettings, setEndSettings] = useState('UNLIMITED');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('00:00');
  const [goalUnits, setGoalUnits] = useState(100);
  const [creativeRotationType, setCreativeRotationType] = useState('EVEN');
  const [roadblockingType, setRoadblockingType] = useState('AS_MANY_AS_POSSIBLE');
  const [customTargeting, setCustomTargeting] = useState([]);
  const [placement, setPlacement] = useState('');
  const [resultado, setResultado] = useState('');
  const [lineItems, setLineItems] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    setLineItems([]);
    setResultado('');

    let deliverySetting = deliverySettings;
    if (deliverySettings === 'CUSTOM') {
      deliverySetting = customDate;
    }

    const response = await fetch('http://127.0.0.1:5000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        orden,
        price,
        limit,
        line_name_template: lineNameTemplate,
        lineItemType: lineItemType.toUpperCase(),
        priority,
        inventoryInclude,
        inventoryExclude,
        expectedCreative,
        deliverySettings: deliverySetting,
        customTime: customTime,
        endSettings: endSettings,
        endDate: endDate,
        endTime: endTime,
        goalUnits: goalUnits,
        creativeRotationType: creativeRotationType,
        roadblockingType: roadblockingType,
        customTargeting,
        placement
      })
    });

    if (response.ok) {
      const data = await response.json();
      setResultado(data.resultado);
      console.log('Response received:', data);
    } else {
      const error = await response.text();
      console.error('Error response:', error);
      setResultado('Error al crear líneas.');
    }
    setIsGenerating(false);
  };

  return (
    <div className="App">
      <h1>Generador de Líneas y Creatividades</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="orden">Order Number:</label>
        <input
          type="text"
          id="orden"
          value={orden}
          onChange={(e) => setOrden(e.target.value)}
          required
        />
        <label htmlFor="lineNameTemplate">Line Name:</label>
        <input
          type="text"
          id="lineNameTemplate"
          value={lineNameTemplate}
          onChange={(e) => setLineNameTemplate(e.target.value)}
          required
        />
        <label htmlFor="lineItemType">Line Type:</label>
        <input
          type="text"
          id="lineItemType"
          value={lineItemType}
          onChange={(e) => setLineItemType(e.target.value.toUpperCase())}
          required
        />
        <label htmlFor="priority">Priority value:</label>
        <input
          type="number"
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          required
        />
        <label htmlFor="expectedCreative">Expected Creative Size:</label>
        <select
          id="expectedCreative"
          value={expectedCreative}
          onChange={(e) => setExpectedCreative(e.target.value)}
          required
        >
          <option value="">Selecciona una opción</option>
          <option value="728x90">728x90</option>
          <option value="1x1">1x1</option>
        </select>
        <label htmlFor="deliverySettings">Delivery Settings:</label>
        <select
          id="deliverySettings"
          value={deliverySettings}
          onChange={(e) => setDeliverySettings(e.target.value)}
          required
        >
          <option value="IMMEDIATELY">IMMEDIATELY</option>
          <option value="CUSTOM">Custom Date and Time</option>
        </select>
        {deliverySettings === 'CUSTOM' && (
          <>
            <input
              type="text"
              id="customDate"
              placeholder="DD/MM/YYYY"
              value={customDate}
              onChange={(e) => setCustomDate(e.target.value)}
              required
            />
            <input
              type="time"
              id="customTime"
              value={customTime}
              onChange={(e) => setCustomTime(e.target.value)}
              required
            />
          </>
        )}
        <label htmlFor="endSettings">End Settings:</label>
        <select
          id="endSettings"
          value={endSettings}
          onChange={(e) => setEndSettings(e.target.value)}
          required
        >
          <option value="UNLIMITED">UNLIMITED</option>
          <option value="CUSTOM">Custom End Date and Time</option>
        </select>
        {endSettings === 'CUSTOM' && (
          <>
            <input
              type="text"
              id="endDate"
              placeholder="DD/MM/YYYY"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
            <input
              type="time"
              id="endTime"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              required
            />
          </>
        )}
        <label htmlFor="goalUnits">Goal (% of total impressions):</label>
        <input
          type="number"
          id="goalUnits"
          value={goalUnits}
          onChange={(e) => setGoalUnits(parseInt(e.target.value))}
          required
        />
        <label htmlFor="creativeRotationType">Rotate creatives:</label>
        <select
          id="creativeRotationType"
          value={creativeRotationType}
          onChange={(e) => setCreativeRotationType(e.target.value)}
          required
        >
          <option value="EVEN">Evenly</option>
          <option value="OPTIMIZED">Optimised</option>
          <option value="WEIGHTED">Weighted</option>
          <option value="SEQUENTIAL">Sequential</option>
        </select>
        <label htmlFor="roadblockingType">Display creatives:</label>
        <select
          id="roadblockingType"
          value={roadblockingType}
          onChange={(e) => setRoadblockingType(e.target.value)}
          required
        >
          <option value="ONLY_ONE">Only one</option>
          <option value="ONE_OR_MORE">One or more</option>
          <option value="AS_MANY_AS_POSSIBLE">As many as possible</option>
          <option value="ALL_ROADBLOCK">All</option>
        </select>
        <label htmlFor="inventoryInclude">Inventory Include:</label>
        <select
          id="inventoryInclude"
          multiple
          value={inventoryInclude}
          onChange={(e) => setInventoryInclude([...e.target.selectedOptions].map(option => option.value))}
        >
          <option value="LV">LV</option>
          <option value="MD">MD</option>
          <option value="RAC1">RAC1</option>
        </select>
        <label htmlFor="inventoryExclude">Inventory Exclude:</label>
        <select
          id="inventoryExclude"
          multiple
          value={inventoryExclude}
          onChange={(e) => setInventoryExclude([...e.target.selectedOptions].map(option => option.value))}
        >
          <option value="comer">Comer</option>
          <option value="historiayvida">Historia y Vida</option>
          <option value="magazine">Magazine</option>
          <option value="motor">Motor</option>
        </select>
        <label htmlFor="customTargeting">Custom Targeting:</label>
        <select
          id="customTargeting"
          multiple
          value={customTargeting}
          onChange={(e) => setCustomTargeting([...e.target.selectedOptions].map(option => option.value))}
        >
          <option value="208473659844">Story Viral</option>
          <option value="189633282084">Story</option>
          <option value="174650883684">Live</option>
        </select>
        <label htmlFor="placement">Placement:</label>
        <select
          id="placement"
          value={placement}
          onChange={(e) => setPlacement(e.target.value)}
          required
        >
          <option value="">Selecciona una opción</option>
          <option value="84198161484">Mega1</option>
        </select>
        <label htmlFor="price">Price:</label>
        <input
          type="number"
          id="price"
          value={price}
          onChange={(e) => setPrice(parseFloat(e.target.value))}
          required
        />
        <label htmlFor="limit">Limit:</label>
        <input
          type="number"
          id="limit"
          value={limit}
          onChange={(e) => setLimit(parseFloat(e.target.value))}
          required
        />
        <button type="submit" disabled={isGenerating}>Crear Línea</button>
      </form>
      {isGenerating && <p>Creando líneas...</p>}
      {resultado && <p>{resultado}</p>}
      <ul>
        {lineItems.map((lineItem) => (
          <li key={lineItem.id}>{lineItem.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
