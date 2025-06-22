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

## High level Design (HLD) 

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
Since this a simple assignment, Infrastructure is outside the scope this design. In real world we would take advantage of scheudling and async process to speed the application further. The applicaiton will be deployed using GCP with the following services, no load balance or auto scaling stragies are needed here.

1. Compute VM : e2-micro , us-central1 , external IP
2. Cloud SQL: Enterpise, Sandbox , us-central1, single zone
3. IP : 1 static IP address

Expected pricing : ~ 88$ - 100$ 

### API Design

Since this backend only application , there is not need to maintain an `/api/v1` prefix or mainatin versioning at this instant. If when the applicaiton is further built for scale all api will be versioned and perfix to differentiate between an api endpoint and ui endpoint.

#### User
The following apis will be developed as part user app.

- `GET /user/` : Get user details
- `POST /user/login/` : Login user and provide a token
- `PUT /organization/` : Create User and orginzation
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

###### Create deployement sequnce diagram

![Create deployment](/docs/assets/create_deployment.png)

### Testing
No speicfic testing pratices is implmemted as part of this assignment.

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


## Low Level design (LLD)

The documents holds the bare bones implmentation of the internal tool `Kargo` django application. Each application will follow the same general principles of the Design. Three domain specific app will be introduce namely user, deployment and clusters. Two code specific apps will be introducted namely core and shared.

- `user` : Responsilble to maintin user domain specific code
- `deployment` :  Responsible to maintain deployment domain specific code
- `cluster` :  Responsible to maintain cluster domain specific code
- `shared` :  Hold shared code to avoid `DRY`, examples include making reverse api class etc.
- `core` : Holds generailzied implentation and sample that are generic but not related to any domnain or implmented. Example include BaseModel, BaseController etc.

The code will be built using SOLID principles to ensure that the application is testable, re-usable, de-coupled and pluggable. Keeping the possible use-case the following main use-cases are identifed for all the programmable logics

- Factory patten to generate service classes and dao classes
- Adapter pattern to control logic building between models and api shapes
- Chain of custody patten for validation and verification
- No native implementation will be avialable but all the object shapes will be declared as struct using `dataclasses`
- `pydantic` will be used for validation and serde.

All the tests will be written and maintained within the app under the folder tests and file specific tests will be maintained. 

Consider the operation of deleteing a deployment, the below example showcase how each pattern will be implmented within the application.

### Adapter pattern
We would have two way to delete a deployment, either through api or through models class. Each implementation will be behind adapter class that hold the core logic

```
# Adapter
class DeploymentAdapter

    def __init__(self):
        pass
    
    @abstractmethod
    def deleteDeployment(self, id):
        pass

class DeploymentApis(DeploymentAdapter):

    def __init__(self):
        pass
    
    def deleteDeployment(self, id):
        # Some api calls

class DeploymentModels(DeployemtnAdapter):

    def __init__(self):
        pass
    
    def deleteDeployment(self, id):
        # Some model class
```

The factor method would provide both the objects maintined in a single class, the factory can return singleton if and when required


### Factory pattern

All the models/logics will be implemented behind a adatper implmentation, the service class will maintained by the implmentation using composition to enable the control and close the implmentation behind a method/class.


```
# Service class with composition 
class DeploymentCrud:
     
    dao = None
    def __init__(self, dao):
        self.adatper = adatper

    def delete_deployment(self, id) -> Boolean:
        return self.adatper.deleteDeploymentById(id)

# Factory pattern
class DeploymentCrudFactory:

    def __init__(self):
        pass

    def create_deployment_crud_with_apid(self) -> DeploymentAdapter:
        api = DeploymentApis()
        return DeploymentCrud(api)

    def create_deployment_crud_with_models(self) -> DeploymentAdapter:
        api = DeploymentModels()
        return DeploymentCrud(api)
```

### Chain of custody 
Each implementation can have different use-cases where data has to be validated before execution, Each such use-case is declared as single class and final usage is chained to verify/validate

```
class AbstractValidate(ABC):

    def __init__(self):
        self._next: Optional[AbstractValidate] = None

    @abstractmethod
    def set_next(self,validate: AbstractValidate ):
        self._next = validate
        return validate

    @abstractmethod
    def validate(self, object) -> Optional[AbstractValidate]:
        if self._next:
            return self._next.validate(object)
        return None
```

Let us assume that we have validator as following `IsClusterPresent`,`BelongToUser` and `SomeOtherValidation`etc.
The validation would similfy somthing 

```
validator = SomeOtherValidation().set_next(IsClusterPresent()).set_next(BelongToUser())
```
This ensures to remove and add validate if and when needed 





