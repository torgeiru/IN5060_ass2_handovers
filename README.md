# Handover time series and comparison 

## Preprocessing  

`python3 create_dataset.py ./location_dataset ./location_dataset_out`

- Day  
- Timestamp  
- QoS Tester_QP Interactivity Progress_Cur. Interactivity Score [%]  
- 5G NR UE_Cell Environment_1. PCI  
- QoS Tester_QP Interactivity Progress_Cur. Num. Lost Packets  

`<input CSV path>`  
├── location_4  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_4_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_7  
│   ├── location_7_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_7_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_7_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_9  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_0.csv  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_1.csv  
|   └── location_9_od_interactivity_egaming_it_tv_tti_2.csv  

`<output CSV path>`  
├── location_4  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_4_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_7  
│   ├── location_7_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_7_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_7_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_9  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_0.csv  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_1.csv  
|   └── location_9_od_interactivity_egaming_it_tv_tti_2.csv   

## Handover detection

`python3 ./capture_handovers.py <input processed CSV path> <output aggregated CSVs path>`  

`<input processed CSV path>`  
├── location_4  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_4_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_7  
│   ├── location_7_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_7_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_7_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_9  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_0.csv  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_1.csv  
|   └── location_9_od_interactivity_egaming_it_tv_tti_2.csv   

`<output aggregated CSVs path>`  
├── location_4_aggregated.csv  
├── location_4_aggregated.json  
├── location_7_aggregated.csv  
├── location_7_aggregated.json  
├── location_9_aggregated.csv  
└── location_9_aggregated.json  

Contents from `location_4_aggregated.json`:  
```json
{
  "location": "location_4",
  "total_handovers": 1,
  "window_size_requested": 100,
  "handover_events": [
    {
      "event_id": 0,
      "source_file": "location_4_od_interactivity_egaming_it_tv_tti_2.csv",
      "handover_index_in_file": 2401,
      "handover_offset_in_window": 50,
      "window_size_requested": 100,
      "window_size_actual": 100,
      "window_start_idx": 2351,
      "window_end_idx": 2451,
      "is_boundary_constrained": false,
      "pci_before": 261,
      "pci_after": 362,
      "pci_column": "5G NR UE_Cell Environment_1. PCI : [1]",
      "handover_timestamp": "10:53:42.102"
    }
  ]
}
```

## Plotting timeseries for handovers in a location  

```
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

```

## Statistical analysis on handovers between locations  

```
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

```