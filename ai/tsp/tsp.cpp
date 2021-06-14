#include <iostream>
#include <cmath>
#include <bits/stdc++.h> 
#include <vector>
#define MAX 500

using namespace std;
//void findMST(float distances[][n], int n);
//void perfectMatching(vector<vector<int> > &adjacencyList, vector<int> &oddVertices, int n);

class City {
    
    public:
    float x;
    float y;
};

class Tour {
    public:
    vector<int> tour;
    float cost;
};

float computeDistance(City c1, City c2) {

    float x=c1.x-c2.x;
    float y=c1.y-c2.y;
    
    float dist=sqrt(x*x+y*y);
    
    return dist;
}

int minDistanceParent(float min_distances[],bool included[], int n) {

    float min=FLT_MAX;
    int min_index;
    for(int i=0;i<n;i++) {
        if(included[i] == false && min_distances[i]<min) {
        	min=min_distances[i];
        	min_index=i;
		}
    }
	
	return min_index;    
}


void eulerTour(vector<int> adjacencyList[],int start, vector<int> &tour, int n) {
    
    vector<int> *temporaryList=new vector<int>[n];
    for(int i=0;i<n;i++) {
        temporaryList[i].resize(adjacencyList[i].size());
		temporaryList[i] = adjacencyList[i];
    }
    
    stack<int> stack;
    int current=start;
    tour.push_back(start);
    
    while(!stack.empty() || temporaryList[current].size()>0 ) {
        
        if(temporaryList[current].empty() ) {
            tour.push_back(current);
            current=stack.top();
            stack.pop();
        }
        
        else  {
            stack.push(current);
            int neighbour= temporaryList[current].back();
            temporaryList[current].pop_back();
            
            for(int i = 0; i < temporaryList[neighbour].size(); i++){
				if(temporaryList[neighbour][i] == current){
					temporaryList[neighbour].erase(temporaryList[neighbour].begin()+i);
				}
			}
			//Set neighbor as current vertex
			current = neighbour;
        }
    } 
    
    tour.push_back(current);
    
//    cout<<"Euler tour : "<<endl;
//    for(int i=0;i<tour.size();i++) {
//        cout<<tour[i]<<" ";
//    }
//    cout<<endl;

}

//Make euler tour Hamiltonian
void hamiltonianTour(vector<vector<float> > distances, vector<int> &tour, float &tourCost, int n){
	//remove visited nodes from Euler tour
	bool visited[n];
	for(int i = 0; i < n; i++){
		visited[i] = false;
	}
	
	tourCost = 0;

	int root = tour.front();
	vector<int>::iterator cur = tour.begin();
	vector<int>::iterator iter = tour.begin()+1;
	visited[root] = true;

	//iterate through circuit
	while(iter != tour.end()){
		if(!visited[*iter]){
			tourCost += distances[*cur][*iter];
			cur = iter;
			visited[*cur] = 1;
			iter = cur + 1;
		}	
		else{
			iter = tour.erase(iter);
		}
	}
	
	//Add distance to root
	tourCost += distances[*cur][*iter];
	
}

void perfectMatching(vector<vector<float> > &distances,vector<int> adjacencyList[], vector<int> &oddVertices, int n) {
    
    int closestVertex;
    float closestDistance;
    
    while(!oddVertices.empty()) {
        
    int u = oddVertices.front();
    vector<int>::iterator it;
    vector<int>::iterator temp;
    closestDistance = FLT_MAX;
    for (it= oddVertices.begin()+1; it < oddVertices.end(); it++) {
      // if this node is closer than the current closest, update closest and length
      if (distances[u][*it] < closestDistance) {
        closestDistance = adjacencyList[u][*it];
        closestVertex = *it;
        temp = it;
      }
    } // two nodes are matched, end of list reached
    
    //bool found=false;
    // for(int i=0;i<adjacencyList[u].size();i++) {
    //     if(adjacencyList[u][i]==closestVertex) {
    //         found=true;
    //     }
    // }
    //if(!found) {
        adjacencyList[u].push_back(closestVertex);
        adjacencyList[closestVertex].push_back(u);
   //}
    oddVertices.erase(temp);
    oddVertices.erase(oddVertices.begin());
    
    }
    
//    cout<<"After perfect matching graph is "<<endl;
//    for (int i = 0; i < n; i++) {
//    	cout << i << ": "; //print which vertex's edge list follows
//    for (int j = 0; j < (int)adjacencyList[i].size(); j++) {
//      	cout << adjacencyList[i][j] << " "; //print each item in edge list
//    	}
//    	cout << endl;
//  	}
  	
  	vector<int> tour;
  	float tourCost;
  	
  	float minCost=FLT_MAX;
  	
  	int minRoot;

    Tour tours[n];
    
    for(int i=0;i<n;i++) {
        eulerTour(adjacencyList, i, tours[i].tour, n);
        hamiltonianTour(distances, tours[i].tour, tours[i].cost, n);
//        if(minCost>tours[i].cost) {
//            minCost=tours[i].cost;
//            minRoot=i;
//        }
    
        if(minCost>tours[i].cost) {
        	minCost=tours[i].cost;
        	for(int j=0;j<tours[i].tour.size();j++) {
	            cout<<tours[i].tour[j]<<" ";
	        }
	        //cout<<"\nCost:"<<tours[i].cost<<endl;
    	}
        else {
        	continue;
		}
		cout<<endl;
		//cout<<"Cost:"<<minCost<<endl;
        
    }

    
//    cout<<"Min root:"<<minRoot<<endl;
//    cout<<"\n Most optimized tour cost : "<<tours[minRoot].cost<<endl;
//    
//    for(int j=0;j<tours[minRoot].tour.size();j++) {
//            cout<<tours[minRoot].tour[j]<<" ";
//        }
//    cout<<endl;

    
}

void findMST(vector<vector<float> > &distances, int n) {
    
    int parent[n];
    float min_distances[n];
    bool included[n];
    
    for(int i=0;i<n;i++) {
        min_distances[i]=FLT_MAX;
        included[i]=false;
    }
    
    min_distances[0]=0.0;
    parent[0]=-1;
    
    for(int c=0;c<n-1;c++) {
    	
    	int u=minDistanceParent(min_distances,included,n);
    	included[u]=true;
    	
	
		for(int i=0;i<n;i++) {
			
			if(distances[u][i] && included[i]==false && distances[u][i]<min_distances[i]) {
				parent[i]=u;
				min_distances[i]=distances[u][i];
			}
		}
	
	}
    //cout<<"In mst"<<endl;
    vector<int> *adjacencyList = new vector<int>[n];
    
    for (int i = 0; i < n; i++) {

    	int j = parent[i];

    	if (j != -1) {

      		adjacencyList[i].push_back(j);
      		adjacencyList[j].push_back(i);

    	}

  	}
  	
//  	cout<<"After mst graph : "<<endl;
//  	for (int i = 0; i < n; i++) {
//     	cout << i << ": "; //print which vertex's edge list follows
//     for (int j = 0; j < (int)adjacencyList[i].size(); j++) {
//      	cout << adjacencyList[i][j] << " "; //print each item in edge list
//     	}
//     	cout << endl;
//  	}
  	
  	//Find vertices with odd degree
  	vector<int> oddVertices;
  	
  	for(int i=0;i<n;i++) {
  		
  		if(adjacencyList[i].size()%2!=0) {
  			oddVertices.push_back(i);
  		}
  	}
  	
//  	cout<<"Odd vertices are "<<endl;
//  	for(int i=0;i<oddVertices.size();i++) {
//  		cout<<oddVertices[i]<<endl;
//  	}
  	
  	perfectMatching(distances,adjacencyList, oddVertices, n);
    
}


void optimizedTour(vector<vector<float> > &distances,City *cities, int n) {

   // vector<vector<float> > newDistances(n);
    for(int i=0;i<distances.size();i++) {
        float temp,temp1;
        for(int j=0;j<n;j++) {
          temp1=computeDistance(cities[i],cities[j]);
          cin>>temp;

        //cout<<temp<<" "<<temp1<<endl;
        //cout<<"temp1:"<<temp1<<endl;
          distances[i].push_back(temp);
         // newDistances[i].push_back(temp1);
        }
    }
    
    //cout<<distances.size()<<endl;
    // cout<<"Distance matrix"<<endl;
    // for(int i=0;i<distances.size();i++) {
    //     //cout<<distances[i].size()<<endl;
    //     for(int j=0;j<distances[i].size();j++) {
    //         cout<<distances[i][j]<<" ";
    //     }
    //     cout<<endl;
    // }

	//cout<<"before entering mst"<<endl;
	//cout<<"Output from distance matrix"<<endl;
	findMST(distances,n);

}


int main() {
	// your code goes here
	string distance_type;
	
	int n;

	getline(cin,distance_type);
	cin>>n;

	City cities[n];
    vector<vector<float> > distances(n);

	for(int i=0;i<n;i++) {
	    
	    cin>>cities[i].x;
	    cin>>cities[i].y;
	    
	}

	//if(distance_type.compare("euclidean") == 0) {
	    optimizedTour(distances,cities,n);
	
	return 0;
}
