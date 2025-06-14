# Project repo
This is a repo for a service application that enables user to deploy appplications to a cluster by providing docker image path.
## Feature list
- Basic auth : User can logged using a basic auth
- Organization : User can create organization 
- Invite code :  User can invite other users to join their organization
- Cluster managment : User can create cluster, track resource and delete
- Deployment managment : User can deploy application to a cluster
- Schedule deployment : User can schedule deployment if and when resource are not available 

# General Design

## SRS
Kargo is an internal platform developed by XYZ Company to enable its teams to deploy services without managing the underlying infrastructure. The tool is designed to simplify the deployment process, reduce the operational overhead of infrastructure setup, and ultimately enhance developer productivity. While the primary users are developers, the platform can also be extended to administrative teams for tasks such as monitoring financials and managing hardware provisioning.

### Functional Requirments
The following feature sets are available and packaged a single service with many apps

1. User Mangement
    - User must be able login username and password
    - User belongs to only one organization
    - User can be added to organization via invite code
    - User need not be register before inviting 
    - Invite code must be a single user and marked as expired after a single use
    - Invite code can be re-open mutliple times
    - Invite code will be expired with respect to time
  
2. Cluser managment
    - Cluster belong to organizations
    - Cluser has resources such as CPU, GPU etc which the system should keep track of
    - User must be able to see the status of cluster at any instant of time
    - Only user belonging to the organization must be able see the clusters
    - Cluster can be deleted if and if there are no deployments for it
    - Cluster once created, cannot be edit with respect to intial resources by the user but can be edit within the system

3. Deployments
    - User can deploy applicaiton by providing docker path
    - User can declare pririty for a deployment
    - higher prority deployment take precedence toward lower prioty deployment
    - Deployments must ensure that max Utilization of the resource of the cluster
    - Limit the number of deployments
    - Deployment can be taken down/ deleted
    - Deployment are deployment to a particular cluster

### Out of scope

Since it a fake system, the following remove out of the scope and would only make sense in a live system. If and when the system is designed for a live, the following will be converted into functional requirments
1. Cluster mangment 
    - status aduit and trail is not maintained
    - Resoruce trail and audit is not maintained 
    - Deploymen status trail and audit is not maintained
2. Deployment
    - Async deplooyment managment 


### Non-functional requirments
- Service must be packaged with docker as containter
- Service should support around 10 users at any instant of time

## HLD 

Kargo is a internal tool that provides the ability for developers to deploy applicaiton. It provides the ability for the developer to declare the resource and deployment applicaiton with ease. To faciliate this process a backend application based on django will be deveploed. The following app will be package as single django application

- User : Resposible for user and organizatiton managment
- Cluster : Reponsible to keep track of cluster and resources
- Deploy : Responsible for deployment mangament

All the apps will communnicate using internal api calls only but never import any of the esstentail object. This ensure that the apps are de-coupled and moveable as module.

### DB Design
The db SQL should be maintained and executed seperately, this ensures that the database is not coupled directly to an applicaiton but coupled to the domain itself. But with time constraint , the applicaiton will be maintaing DB, if time permits this will be moved out the application at later point of the time.

![DB design](/docs/assets/db.png)

- User table is responsible to hold details of the user such as username, password and any other metadata related to the user
- Each user belong to a single organization but organizaitons can have multiple users
- Organization table is responsible to hold details of the organization such name and any other meta data
- Invitecode table is resposible to keep track of the invite code generated, usage of the codes and connectivity of organization and user. 
    - The table keeps track of the which user has used the code.
    - The table keeps track of the expiry time of the code 
    - The table keeps track whether a code has been used or expired 
    - A code is consider expired if expired is true but used_by is null
    - A code is consider used if  expired is true and used_by is not null
-  Cluster table keeps track of the cluster details and connectivty with respect to orgnizaiton. It also holds id of the user who created for audit purpose
- Resource table is flat table that hold resource details of a cluster
    - Each resoruce type of the cluster is maintined
    - Instead of column based arch , a row based design will save space as not all cluster have cpu and gpu need. Some only have cpu need and some only have gpu need.
    - The current value of the resource is also maintained.
- Deployment table is responsible for keeping track of deployment
    - The table keeps track of prority 
    - The table keeps track of status 

### Infrastructure 
Since this a simple assignment, Infrastructure is outside the scope this design. In real world we would take advantage of scheudling and async process to speed the application further.

### API Design

Since this backend only application , there is not need to maintain an `/api/v1` prefix or mainatin versioning at this instant. If when the applicaiton is further built for scale all api will be versioned and perfix to differentiate between an api endpoint and ui endpoint.

#### User
The following apis will be developed as part user app.

- `GET /user/` : Get user details
- `PUT /user/create/` : Create User and orginzation
- `POST /user/login/` : Login user and provide a token
- `GET /organization/`: Get organization details
- `PATCH /organization/invite/` : Generate organization invite code
- `GET /organization/invite/?code=` : Verify if the code is active
- `POST /organization/invite/` : User organization invite code

Since this there no external dependency on the other applicaiton, there is no specific sequence diagrams needed. The above endpoints are esstential simple CRUD endpoints. All the end points apart from the login and create will have auth headers prevert the mis-use of the endpoints.

An auth middleware will be developed to convert a give header token into user and org id, these will be added as part of the post request for the rest of the application to read and process , if and when needed.

#### Cluster
The following apis will be developed as part of the cluster app

- `GET /cluster/?page=<int>&offset=<int>`:  Get clusters that the user has access to , paginated
- `GET /cluster/<pk>/` :  Get details of the cluster such as resource and current usage
- `PUT /cluster/` : Create a new cluster with resources
- `DELETE /cluster/<pk>/`:  Delete an existing cluster
- `PATCH /cluster/<pk>/resource/` : Check if the cluster has the required resources
- `POST /cluster/<pk>/resource/` : Utilize resouce
- `DELETE /cluster/<pk>/resource/` : Free up resource

##### Delete cluster sequence diagram

![Delete cluster flow](/docs/assets/delete_cluster_flow.png)

#### Deployment
The following apis will be developed as part of the the deployment app

- `GET /deployment/?cluster_id=<id>` :  Get current deployments, paginated 
- `PUT /deployment/` : Create deployment for a cluster
- `DELETE /deployment/<pk>/` : Delete deployment 
- `DELETE /deployment/?clusterId=<id>` : Delete deployment 

###### Create deployment

![Create deployment](/docs/assets/create_deployment.png)

##### Create deployement sequnce diagram
### Appendix

#### Get user details

```
curl --location 'http://localhost:8001/user/login/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "Sample",
    "password": "Sample"
}'
```

#### Create User and organization

```
curl --location --request PUT 'http://localhost:8001/user/create/' \
--header 'Content-Type: application/json' \
--data '{
    "user": {
        "username": "Sample",
        "password": "Sample",
        "display_name": "Sample"
    },
    "organization": {
        "name": "Sample"
    }
}'
```

#### Login User

```
curl --location 'http://localhost:8001/user/login/' \
--header 'Content-Type: application/json' \
--data '{
    "username": "Sample",
    "password": "Sample"
}'
```

#### Get user details

```
curl --location 'http://localhost:8001/user/' \
--header 'Authorization: Bearer test'
```

#### Get Organization details

```
curl --location 'http://localhost:8001/organization/' \
--header 'Authorization: Bearer test'
```

#### Generate Invite

```
curl --location --request PATCH 'http://localhost:8001/organization/invite/' \
--header 'Authorization: Bearer test' \
--data ''
```

#### Use invite code

```
curl --location 'http://localhost:8001/organization/invite/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "username": "Sample",
    "password": "Sample",
    "display_name": "Sample"
}'
```

#### Get cluster

```
curl --location 'http://localhost:8001/cluster/?page=0&offset=1' \
--header 'Authorization: Bearer test'
```

#### Get cluster details

```
curl --location 'http://localhost:8001/cluster/:id/' \
--header 'Authorization: Bearer test'
```


#### Create cluster

```
curl --location --request PUT 'http://localhost:8001/cluster/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "cluster_name": "name",
    "resource": {
        "cpu": "1",
        "gpu": "1",
        "ram": " 1"
    }
}'
```

#### Delete cluster
```
curl --location --request DELETE 'http://localhost:8001/cluster/:id/' \
--header 'Authorization: Bearer test'
```

#### Check cluster for resources
```
curl --location --request PATCH 'http://localhost:8001/cluster/:cluster_id/resource/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "resource": {
        "cpu": "1",
        "gpu": "1",
        "ram": " 1"
    }
}'
```

#### Utilize resources
```
curl --location 'http://localhost:8001/cluster/:cluster_id/resource/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "resource": {
        "cpu": "1",
        "gpu": "1",
        "ram": " 1"
    }
}'
```

#### Free up resources
```
curl --location --request DELETE 'http://localhost:8001/cluster/:cluster_id/resource/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "resource": {
        "cpu": "1",
        "gpu": "1",
        "ram": " 1"
    }
}'
```

#### Get deployment
```
curl --location 'http://localhost:8001/deployment/?cluster_id=11&id=1' \
--header 'Authorization: Bearer test'
```

#### Create deployment for a cluster

```
curl --location --request PUT 'http://localhost:8001/deployment/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer test' \
--data '{
    "cluster_id": "1",
    "resource": {
        "gpu": 1,
        "cpu": 1,
        "ram": 1
    }
}'
```

#### Delete deployment

```
curl --location --request DELETE 'http://localhost:8001/deployment/:id/' \
--header 'Authorization: Bearer test' \
--data ''
```


