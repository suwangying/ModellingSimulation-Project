# Elevator Simulation Experiment Questions
The purpose of these experiments is to evaluate how elevator dispatch strategies affect passenger wait times and system efficiency.

## Key Questions
1. Which dispatch policy produces the lowest mean passenger wait time during morning up-peak traffic?
Under the morning up-peak scenario (λ = 0.05, 2 elevators), all three dispatch policies — nearest, zoning, and up-peak bias — produced identical mean wait times of approximately 5.5 seconds.
This occurs because all passengers originate from the lobby (floor 0), resulting in a single shared pickup location. As a result, all policies make effectively the same decision, causing their performance to converge.
Therefore, no single policy outperforms the others under this scenario, and dispatch strategy has minimal impact when passenger demand is highly centralized.

2. Which policy minimizes the 95th percentile wait time, representing worst-case passenger experience?
The policy that minimizes the 95th percentile wait time depends on the traffic scenario. In the up-peak scenario, all three policies perform almost identically because demand is concentrated at the lobby. In the midday scenario, the nearest-pickup policy gives the lowest worst-case wait time, while zoning and up-peak bias are slightly worse. In the down-peak scenario, nearest and up-peak bias perform similarly and both outperform zoning. Overall, the nearest-pickup policy is the most consistent policy for minimizing worst-case passenger wait across scenarios.

3. How does increasing the number of elevators (1–4) affect average waiting time?
Increasing the number of elevators reduces the average passenger waiting time, as more requests can be served simultaneously. The most significant improvement occurs when increasing from one to two elevators. Additional elevators continue to reduce waiting time, but the benefit diminishes with each added elevator. The results show that the waiting time stabilizes after approximately 3 to 4 elevators, indicating that adding more elevators beyond this point provides minimal improvement. This demonstrates a clear diminishing returns effect and suggests that 3–4 elevators are sufficient for the given system and demand conditions.

4. How do different policies affect elevator utilization?
The results show that elevator utilization varies significantly with traffic patterns but remains nearly unchanged across different dispatch policies. Utilization is lowest during the up-peak scenario and increases during midday and down-peak traffic due to higher demand and more frequent elevator usage. However, policies such as nearest-pickup, zoning, and up-peak bias do not significantly affect utilization because they do not change the total number of passengers or the overall workload. Instead, these policies primarily influence passenger waiting times rather than system workload.

5. Does zoning reduce congestion compared to the nearest-pickup strategy?
The results show that zoning does not significantly reduce congestion compared to the nearest-pickup strategy. In the up-peak scenario, all policies produce identical queue lengths due to highly centralized demand at the lobby. In the midday scenario, the nearest-pickup policy slightly outperforms zoning, as it allows more flexible servicing of distributed requests. In the down-peak scenario, zoning shows a marginal improvement, but the difference is minimal. Overall, zoning does not provide a meaningful reduction in congestion under the tested conditions.

6. How does traffic pattern (up-peak vs midday inter-floor) affect system performance?
Traffic patterns significantly affect system performance. During up-peak traffic, where most passengers originate from the lobby, the system experiences high congestion and long queues due to concentrated demand at a single floor. In contrast, midday inter-floor traffic results in lower queue lengths and more balanced elevator utilization, as requests are distributed across multiple floors. Down-peak traffic shows higher utilization but moderate congestion. Overall, distributed traffic patterns (midday) lead to more efficient system performance compared to highly concentrated patterns (up-peak).

7. Is there a trade-off between low waiting times and high elevator utilization?
There is a partial trade-off between passenger wait time and elevator utilization. In the up-peak scenario, wait times are relatively low while utilization is also very low, indicating underused elevator capacity. In contrast, during down-peak traffic, higher utilization corresponds to slightly increased wait times, suggesting a trade-off between efficiency and service quality. However, in the midday scenario, both low wait times and moderate utilization are achieved simultaneously, indicating that efficient system performance is possible when demand is well distributed. Overall, the trade-off exists but is influenced by traffic patterns.

8. At what passenger arrival rate does the system begin to experience significant queue buildup?
The system begins to experience significant queue buildup at approximately λ = 0.05 passengers per second. At this point, the average queue length increases sharply from around 18 to over 70, indicating that the passenger arrival rate begins to exceed the service capacity of the elevators. Beyond this threshold, queue length continues to grow rapidly as demand increases.
