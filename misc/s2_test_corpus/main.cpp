// Copyright 2020 Adam Liddell
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <numeric>
#include <iostream>
#include <fstream>
#include "s2/s2cell_id.h"
#include "s2/s2latlng.h"


// This writes three files that contain a set of test data from the reference C++ S2 implementation:
//
// - s2_encode_corpus.csv:
//   lat, lon, level, encoded cell ID
//
// - s2_decode_corpus.csv:
//   cell_id, decoded lat, decoded lon, decoded level
//
// - s2_neighbor_corpus.csv:
//   cell_id,neighbors
//
int main(int argc, char **argv) {
    // Config
    int steps = 60;

    // Open files
    std::ofstream encode_file{}, decode_file{}, neighbor_file{};

    encode_file.open("s2_encode_corpus.csv");
    encode_file.precision(17);
    encode_file << "lat,lon,level,cell_id,token\n";

    decode_file.open("s2_decode_corpus.csv");
    decode_file.precision(17);
    decode_file << "cell_id,token,lat,lon,level\n";

    neighbor_file.open("s2_neighbor_corpus.csv");
    neighbor_file.precision(17);
    neighbor_file << "cell_id,edge_neighbors,all_neighbors\n";

    // Generate data
    for (int lat_idx = 0; lat_idx < steps; lat_idx++) {
        for (int lon_idx = 0; lon_idx < steps; lon_idx++) {
            // Create S2LatLng and leaf cell
            double lat = ((double)lat_idx / (steps - 1)) * 180.0 - 90.0;
            double lon = ((double)lon_idx / (steps - 1)) * 360.0 - 180.0;
            auto latlon = S2LatLng::FromDegrees(lat, lon);
            auto leaf_cell = S2CellId(latlon);

            for (int level = 0; level <= 30; level++) {
                // Get cell for specified level
                auto level_cell = leaf_cell.parent(level);
                auto cell_id = level_cell.id();
                auto token = level_cell.ToToken();
                encode_file << lat << "," << lon << "," << level << "," << cell_id << "," << token << "\n";

                // Decode cell ID back to lat lon
                auto decoded_latlon = level_cell.ToLatLng();
                auto dlat = decoded_latlon.lat().degrees();
                auto dlon = decoded_latlon.lng().degrees();
                auto dlevel = level_cell.level();
                decode_file << cell_id << "," << token << "," << dlat << "," << dlon << "," << dlevel << "\n";
            
                // Find cell neighbors
                S2CellId edge_neighbors[4];
                level_cell.GetEdgeNeighbors(edge_neighbors);

                std::vector<S2CellId> all_neighbors;
                level_cell.AppendAllNeighbors(level, &all_neighbors);

                neighbor_file << cell_id << "," << std::accumulate(
                    std::begin(edge_neighbors), std::end(edge_neighbors), std::string{},
                    [](std::string &s, S2CellId neigh_cell) {
                        if (!s.empty()) s += ":";
                        return s + std::to_string(neigh_cell.id());
                    }) << "," << std::accumulate(
                    std::begin(all_neighbors), std::end(all_neighbors), std::string{},
                    [](std::string &s, S2CellId neigh_cell) {
                        if (!s.empty()) s += ":";
                        return s + std::to_string(neigh_cell.id());
                    }) << "\n";
            }
        }
    }

    // Close files
    encode_file.close();
    decode_file.close();
    neighbor_file.close();

    return 0;
}
