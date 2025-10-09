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

Contents from `location_4_aggregated.csv`:  
```csv
handover_event_id;row_in_window;is_handover_point;Day;Timestamp [dd.mm.yyyy,hh:mm:ss.ss];5G NR UE_Cell Environment_1. PCI : [1];QoS Tester_QP Interactivity Progress_Cur. Num. Lost Packets : [1];QoS Tester_QP Interactivity Progress_Cur. Interactivity Score [%] : [1]
0;0;False;05.07.2023;10:53:39.511;261;0;82.5
0;1;False;05.07.2023;10:53:39.681;261;0;82.5
0;2;False;05.07.2023;10:53:39.707;261;0;82.5
0;3;False;05.07.2023;10:53:39.746;261;0;82.5
0;4;False;05.07.2023;10:53:39.770;261;0;82.5
0;5;False;05.07.2023;10:53:39.824;261;0;82.5
0;6;False;05.07.2023;10:53:39.907;261;0;81.5
0;7;False;05.07.2023;10:53:39.944;261;0;81.5
0;8;False;05.07.2023;10:53:39.997;261;0;81.5
0;9;False;05.07.2023;10:53:40.000;261;0;81.5
0;10;False;05.07.2023;10:53:40.010;261;0;81.5
0;11;False;05.07.2023;10:53:40.175;261;0;81.5
0;12;False;05.07.2023;10:53:40.319;261;0;81.5
0;13;False;05.07.2023;10:53:40.422;261;0;81.5
0;14;False;05.07.2023;10:53:40.422;261;0;81.5
0;15;False;05.07.2023;10:53:40.425;261;0;81.5
0;16;False;05.07.2023;10:53:40.500;261;0;81.5
0;17;False;05.07.2023;10:53:40.510;261;0;81.5
0;18;False;05.07.2023;10:53:40.511;261;0;81.5
0;19;False;05.07.2023;10:53:40.696;261;0;81.5
0;20;False;05.07.2023;10:53:40.707;261;0;81.5
0;21;False;05.07.2023;10:53:40.741;261;0;81.5
0;22;False;05.07.2023;10:53:40.785;261;0;81.5
0;23;False;05.07.2023;10:53:40.903;261;0;81.5
0;24;False;05.07.2023;10:53:40.914;261;0;82.8
0;25;False;05.07.2023;10:53:40.935;261;0;82.8
0;26;False;05.07.2023;10:53:41.000;261;0;82.8
0;27;False;05.07.2023;10:53:41.010;261;0;82.8
0;28;False;05.07.2023;10:53:41.036;261;0;82.8
0;29;False;05.07.2023;10:53:41.173;261;0;82.8
0;30;False;05.07.2023;10:53:41.313;261;0;82.8
0;31;False;05.07.2023;10:53:41.313;261;0;82.8
0;32;False;05.07.2023;10:53:41.423;261;0;82.8
0;33;False;05.07.2023;10:53:41.423;261;0;82.8
0;34;False;05.07.2023;10:53:41.427;261;0;82.8
0;35;False;05.07.2023;10:53:41.501;261;0;82.8
0;36;False;05.07.2023;10:53:41.510;261;0;82.8
0;37;False;05.07.2023;10:53:41.558;261;0;82.8
0;38;False;05.07.2023;10:53:41.676;261;0;82.8
0;39;False;05.07.2023;10:53:41.725;261;0;82.8
0;40;False;05.07.2023;10:53:41.755;261;0;82.8
0;41;False;05.07.2023;10:53:41.756;261;0;82.8
0;42;False;05.07.2023;10:53:41.756;261;0;82.8
0;43;False;05.07.2023;10:53:41.816;261;0;82.8
0;44;False;05.07.2023;10:53:41.887;261;0;82.8
0;45;False;05.07.2023;10:53:41.899;261;0;0.0
0;46;False;05.07.2023;10:53:41.899;261;0;0.0
0;47;False;05.07.2023;10:53:41.951;261;0;0.0
0;48;False;05.07.2023;10:53:42.000;261;0;0.0
0;49;False;05.07.2023;10:53:42.010;261;0;0.0
0;50;True;05.07.2023;10:53:42.102;362;0;0.0
0;51;False;05.07.2023;10:53:42.173;362;0;0.0
0;52;False;05.07.2023;10:53:42.434;362;0;0.0
0;53;False;05.07.2023;10:53:42.435;362;0;0.0
0;54;False;05.07.2023;10:53:42.438;362;0;0.0
0;55;False;05.07.2023;10:53:42.500;362;0;0.0
0;56;False;05.07.2023;10:53:42.510;362;0;0.0
0;57;False;05.07.2023;10:53:42.622;362;0;0.0
0;58;False;05.07.2023;10:53:42.694;362;0;0.0
0;59;False;05.07.2023;10:53:42.781;362;0;0.0
0;60;False;05.07.2023;10:53:42.781;362;0;0.0
0;61;False;05.07.2023;10:53:42.837;362;0;0.0
0;62;False;05.07.2023;10:53:42.840;362;0;0.0
0;63;False;05.07.2023;10:53:43.001;362;0;0.0
0;64;False;05.07.2023;10:53:43.011;362;0;0.0
0;65;False;05.07.2023;10:53:43.095;362;0;0.0
0;66;False;05.07.2023;10:53:43.096;362;0;0.0
0;67;False;05.07.2023;10:53:43.132;362;0;0.0
0;68;False;05.07.2023;10:53:43.137;362;0;0.0
0;69;False;05.07.2023;10:53:43.174;362;0;0.0
0;70;False;05.07.2023;10:53:43.432;362;0;0.0
0;71;False;05.07.2023;10:53:43.432;362;0;0.0
0;72;False;05.07.2023;10:53:43.434;362;0;0.0
0;73;False;05.07.2023;10:53:43.500;362;0;0.0
0;74;False;05.07.2023;10:53:43.510;362;0;0.0
0;75;False;05.07.2023;10:53:43.645;362;0;0.0
0;76;False;05.07.2023;10:53:43.688;362;0;0.0
0;77;False;05.07.2023;10:53:43.746;362;0;0.0
0;78;False;05.07.2023;10:53:43.746;362;0;0.0
0;79;False;05.07.2023;10:53:43.840;362;0;0.0
0;80;False;05.07.2023;10:53:43.845;362;0;0.0
0;81;False;05.07.2023;10:53:43.972;362;0;0.0
0;82;False;05.07.2023;10:53:44.000;362;0;0.0
0;83;False;05.07.2023;10:53:44.010;362;0;0.0
0;84;False;05.07.2023;10:53:44.103;362;0;0.0
0;85;False;05.07.2023;10:53:44.162;362;0;0.0
0;86;False;05.07.2023;10:53:44.189;362;0;0.0
0;87;False;05.07.2023;10:53:44.489;362;0;0.0
0;88;False;05.07.2023;10:53:44.497;362;0;0.0
0;89;False;05.07.2023;10:53:44.499;362;0;0.0
0;90;False;05.07.2023;10:53:44.499;362;0;0.0
0;91;False;05.07.2023;10:53:44.500;362;0;0.0
0;92;False;05.07.2023;10:53:44.500;362;0;0.0
0;93;False;05.07.2023;10:53:44.501;362;0;0.0
0;94;False;05.07.2023;10:53:44.503;362;0;0.0
0;95;False;05.07.2023;10:53:44.504;362;0;0.0
0;96;False;05.07.2023;10:53:44.507;362;0;0.0
0;97;False;05.07.2023;10:53:44.510;362;0;0.0
0;98;False;05.07.2023;10:53:44.539;362;0;0.0
0;99;False;05.07.2023;10:53:44.650;362;0;0.0
```

## Plotting timeseries for handovers in a location  

`python3 ./handover_timeseries_plot.py <input handover data folder> <output timeseries plots folder>`  

`<input handover data folder>`:  
├── location_4_aggregated.csv  
├── location_4_aggregated.json  
├── location_7_aggregated.csv  
├── location_7_aggregated.json  
├── location_9_aggregated.csv  
└── location_9_aggregated.json  

`<output timeseries plots folder>`:  
├── location_4_aggregated.png  
├── location_7_aggregated.png  
└── location_9_aggregated.png  

## Statistical analysis on handovers between locations  

```
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

```