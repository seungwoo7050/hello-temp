print("Attempting to initialize replica set and create users...");

const rsConfig = {
    _id: "rs0",
    members: [
        { _id: 0, host: "mongo1:27017", priority: 3 },
        { _id: 1, host: "mongo2:27017", priority: 2 },
        { _id: 2, host: "mongo3:27017", priority: 1 }
    ]
};

let rsStatus;
try {
    rsStatus = rs.status();
    print("Replica set already initialized.");
    printjson(rsStatus);
} catch (e) {
    if (e.message && (e.message.includes("no replset config") || e.message.includes("not usable for replica sets") || e.codeName === 'NotYetInitialized')) {
        print("Initializing replica set...");
        const initResult = rs.initiate(rsConfig);
        print("Replica set initiation result:");
        printjson(initResult);
        print("Waiting for replica set to have a primary...");
        let attempts = 0;
        const maxAttempts = 30; 
        while (attempts < maxAttempts) {
            try {
                rsStatus = rs.status();
                if (rsStatus.myState === 1) { 
                    print("Primary elected.");
                    break;
                }
            } catch (err) {
                
            }
            print(`Still waiting for primary... attempt ${attempts + 1}/${maxAttempts}`);
            sleep(1000); 
            attempts++;
        }
        if (attempts === maxAttempts) {
            print("Failed to confirm primary election in time. Please check replica set status manually.");
        }

    } else {
        print("Error checking replica set status, potentially already configured or other issue:");
        printjson(e);
        
    }
}

print("Primary election should be complete. Proceeding with user and database creation if not already done.");
const appDbName = "app_specific_db";
const appUserName = "app_user";
const appUserPassword = "app_password_123"; 
db = db.getSiblingDB('admin');
let userExists = db.getUser(appUserName);
if (!userExists) {
    print(`User ${appUserName} does not exist. Creating user...`);
    db.getSiblingDB(appDbName).createUser({
        user: appUserName,
        pwd: appUserPassword,
        roles: [
            { role: "readWrite", db: appDbName },
            { role: "read", db: "another_db_if_needed" } 
        ]
    });
    print(`User ${appUserName} created for database ${appDbName}.`);
} else {
    print(`User ${appUserName} already exists.`);
}
const anotherAppDbName = "service_b_db";
const anotherAppUser = "service_b_user";
const anotherAppPassword = "service_b_secure_password";
userExists = db.getUser(anotherAppUser);
if(!userExists) {
    print(`User ${anotherAppUser} does not exist. Creating user...`);
    db.getSiblingDB(anotherAppDbName).createUser({
        user: anotherAppUser,
        pwd: anotherAppPassword,
        roles: [{ role: "readWrite", db: anotherAppDbName }]
    });
    print(`User ${anotherAppUser} created for database ${anotherAppDbName}.`);
} else {
    print(`User ${anotherAppUser} already exists.`);
}
print("MongoDB initialization script finished.");