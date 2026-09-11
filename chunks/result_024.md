Dưới đây là interface `CollaboratorService`, định nghĩa các thao tác đơn giản của Anticorruption Layer (ACL - lớp chống tha hóa, giúp bảo vệ mô hình miền khỏi sự xâm nhập của mô hình ngoại lai):

```java
public interface CollaboratorService {
    public Author authorFrom(Tenant aTenant, String anIdentity);
    public Creator creatorFrom(Tenant aTenant, String anIdentity);
    public Moderator moderatorFrom(Tenant aTenant, String anIdentity);
    public Owner ownerFrom(Tenant aTenant, String anIdentity);
    public Participant participantFrom(Tenant aTenant, String anIdentity);
}

```

Dưới góc nhìn của các client sử dụng `CollaboratorService`, interface này đã trừu tượng hóa hoàn toàn sự phức tạp của việc truy cập hệ thống từ xa cũng như các bước chuyển dịch tiếp theo từ Published Language (ngôn ngữ chuẩn công bố giữa các hệ thống) sang các đối tượng tuân thủ Ubiquitous Language (ngôn ngữ chung / toàn hiện) của miền cục bộ. Trong trường hợp cụ thể này, chúng tôi áp dụng mẫu thiết kế Separated Interface (tách biệt giao diện khỏi phần triển khai) [Fowler, P of EAA] cùng một lớp triển khai riêng, bởi việc hiện thực hóa này thuần túy mang tính kỹ thuật và không nên tồn tại trong Domain Layer (tầng nghiệp vụ / tầng miền).

Tất cả các Factory (phương thức / lớp nhà máy khởi tạo đối tượng) (11) này đều rất giống nhau. Chúng đều tạo ra một lớp con kế thừa từ kiểu trừu tượng Collaborator Value Object (đối tượng giá trị), nhưng chỉ khi user thuộc `aTenant` và sở hữu `anIdentity` đảm nhận vai trò bảo mật thuộc một trong năm kiểu sau: `Author`, `Creator`, `Moderator`, `Owner` và `Participant`. Do chúng tương tự nhau, chúng ta hãy cùng xem xét phần triển khai của một phương thức tiêu biểu là `authorFrom()`:

```java
package com.saasovation.collaboration.infrastructure.services;

import com.saasovation.collaboration.domain.model.collaborator.Author;
...

public class TranslatingCollaboratorService implements CollaboratorService {
    ...
    @Override
    public Author authorFrom(Tenant aTenant, String anIdentity) {
        Author author =

```

## INTEGRATION USING RESTFUL RESOURCES

```java
            this.userInRoleAdapter.toCollaborator(
                aTenant,
                anIdentity,
                "Author",
                Author.class);

        return author;
    }
    ...
}

```

Trước tiên, hãy lưu ý rằng `TranslatingCollaboratorService` nằm trong một Module (mô-đun đóng gói mã nguồn) (9) thuộc tầng Infrastructure (hạ tầng kỹ thuật). Chúng tôi định nghĩa Separated Interface bên trong hình lục giác nội tại như một phần của mô hình miền nghiệp vụ. Tuy nhiên, phần triển khai lại mang tính kỹ thuật nên được đặt ở bên ngoài kiến trúc Hexagonal (kiến trúc lục giác), nơi các Ports and Adapters (cổng và bộ điều hợp) cư ngụ.

Xét về mặt kỹ thuật, một Anticorruption Layer thông thường sẽ bao gồm một Adapter chuyên biệt [Gamma et al.] và một translator (bộ dịch mã). Nhìn lại Hình 13.1, bạn có thể thấy Adapter cụ thể ở đây là `UserInRoleAdapter`, còn bộ dịch mã là `CollaboratorTranslator`. Lớp `UserInRoleAdapter` chuyên biệt của Anticorruption Layer này chịu trách nhiệm kết nối tới hệ thống từ xa để yêu cầu resource user-in-role cần thiết:

```java
package com.saasovation.collaboration.infrastructure.services;

import org.jboss.resteasy.client.ClientRequest;
import org.jboss.resteasy.client.ClientResponse;
...

public class UserInRoleAdapter {
    ...
    public <T Collaborator extends> T toCollaborator(
        Tenant aTenant,
        String anIdentity,
        String aRoleName,
        Class<T> aCollaboratorClass) {

        T collaborator = null;

        try {
            ClientRequest request = this.buildRequest(aTenant, anIdentity, aRoleName);
            ClientResponse<String> response = request.get(String.class);

            if (response.getStatus() == 200) {
                collaborator = new CollaboratorTranslator()

```

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
                    .toCollaboratorFromRepresentation(
                        response.getEntity(),
                        aCollaboratorClass);
            } else if (response.getStatus() != 204) {
                throw new IllegalStateException(
                    "There was a problem requesting the user: "
                    + anIdentity
                    + " in role: "
                    + aRoleName
                    + " with resulting status: "
                    + response.getStatus());
            }
        } catch (Throwable t) {
            throw new IllegalStateException(
                "Failed because: " + t.getMessage(),
                t);
        }

        return collaborator;
    }
    ...
}

```

Nếu phản hồi cho yêu cầu GET thành công (mã trạng thái 200), điều đó đồng nghĩa với việc `UserInRoleAdapter` đã nhận được resource biểu diễn user-in-role, và giờ đây resource này có thể được chuyển dịch thành lớp con của `Collaborator`:

```java
package com.saasovation.collaboration.infrastructure.services;

import java.lang.reflect.Constructor;
import com.saasovation.common.media.RepresentationReader;
...

public class CollaboratorTranslator {

    public CollaboratorTranslator() {
        super();
    }

    public <T Collaborator extends> T toCollaboratorFromRepresentation(
        String aUserInRoleRepresentation,
        Class<T> aCollaboratorClass) throws Exception {

        RepresentationReader reader = new RepresentationReader(aUserInRoleRepresentation);
        String username = reader.stringValue("username");
        String firstName = reader.stringValue("firstName");
        String lastName = reader.stringValue("lastName");
        String emailAddress = reader.stringValue("emailAddress");

```

## INTEGRATION USING RESTFUL RESOURCES

```java
        T collaborator = this.newCollaborator(
            username,
            firstName,
            lastName,
            emailAddress,
            aCollaboratorClass);

        return collaborator;
    }

    private <T Collaborator extends> T newCollaborator(
        String aUsername,
        String aFirstName,
        String aLastName,
        String aEmailAddress,
        Class<T> aCollaboratorClass) throws Exception {

        Constructor<T> ctor = aCollaboratorClass.getConstructor(
            String.class,
            String.class,
            String.class);

        T collaborator = ctor.newInstance(
            aUsername,
            (aFirstName + " " + aLastName).trim(),
            aEmailAddress);

        return collaborator;
    }
}

```

Bộ dịch mã này nhận vào một chuỗi `String` biểu diễn dữ liệu văn bản user-in-role cùng với kiểu `Class` dùng để tạo instance của lớp con `Collaborator`. Đầu tiên, lớp `RepresentationReader` — có cơ chế tương tự như `NotificationReader` đã giới thiệu trước đó — được dùng để trích xuất bốn thuộc tính từ định dạng JSON. Chúng ta hoàn toàn có thể tự tin và yên tâm thực hiện điều này vì custom media type của SaaSOvation đã đóng vai trò là một giao kèo liên kết (binding contract) chặt chẽ giữa bên cung cấp (producer) và bên tiêu thụ (consumer). Sau khi bộ dịch có được các giá trị chuỗi cần thiết, nó sẽ dùng chúng để khởi tạo Collaborator Value Object, mà trong ví dụ cụ thể này là một `Author`:

```java
package com.saasovation.collaboration.domain.model.collaborator;

public final class Author extends Collaborator {

```

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
    public Author(
        String anIdentity,
        String aName,
        String anEmailAddress) {
        super(anIdentity, aName, anEmailAddress);
    }
    ...
}

```

Hệ thống hoàn toàn không cố gắng duy trì đồng bộ các instance Collaborator Value Object với Identity and Access Context (Ngữ cảnh Định danh và Truy cập). Chúng là các đối tượng bất biến (immutable) và chỉ có thể được thay thế toàn bộ chứ không thể sửa đổi từng phần. Dưới đây là cách mà một Application Service (dịch vụ ứng dụng điều phối use case) lấy một `Author` ra và truyền vào `Forum` để bắt đầu một cuộc thảo luận `Discussion` mới:

```java
package com.saasovation.collaboration.application;
...

public class ForumService ... {
    ...
    @Transactional
    public Discussion startDiscussion(
        String aTenantId,
        String aForumId,
        String anAuthorId,
        String aSubject) {

        Tenant tenant = new Tenant(aTenantId);
        ForumId forumId = new ForumId(aForumId);
        Forum forum = this.forum(tenant, forumId);

        if (forum == null) {
            throw new IllegalStateException("Forum does not exist.");
        }

        Author author = this.collaboratorService.authorFrom(
            tenant,
            anAuthorId);

        Discussion newDiscussion = forum.startDiscussion(
            this.forumNavigationService(),
            author,
            aSubject);

        this.discussionRepository.add(newDiscussion);

        return newDiscussion;
    }
    ...
}

```

Nếu tên hoặc địa chỉ email của một `Collaborator` thay đổi trong Identity and Access Context, những thay đổi đó sẽ không tự động cập nhật trong Collaboration Context. Những dạng thay đổi này rất hiếm khi xảy ra, vì vậy nhóm phát triển đã quyết định giữ cho thiết kế này đơn giản và không cố đồng bộ các thay đổi từ Context từ xa với các đối tượng trong Context cục bộ của mình. Tuy nhiên, chúng ta sẽ thấy rằng Agile Project Management Context lại có các mục tiêu thiết kế hoàn toàn khác.

Ngoài ra còn có nhiều cách khác để triển khai Anticorruption Layer, chẳng hạn như thông qua Repository (kho lưu trữ và tái tạo Aggregate) (12). Tuy nhiên, vì các Repository thường được dùng để lưu trữ bền vững và tái tạo các Aggregate (cụm đối tượng liên kết có ranh giới nhất quán), nên việc dùng nó để tạo Value Object có vẻ không đúng chỗ. Nếu mục tiêu của chúng ta là tạo ra một Aggregate từ Anticorruption Layer, thì Repository mới là nguồn phát sinh tự nhiên và phù hợp hơn.

## Tích hợp bằng cơ chế gửi thông điệp (Integration Using Messaging)

Cách tiếp cận tích hợp dựa trên thông điệp (message-based) cho phép một hệ thống đạt được mức độ độc lập (autonomy) cao hơn đối với các hệ thống mà nó phụ thuộc. Miễn là hạ tầng gửi thông điệp vẫn duy trì hoạt động bình thường, các thông điệp vẫn có thể được gửi và chuyển giao thành công ngay cả khi một hệ thống bất kỳ nào đó tạm thời không khả dụng.

Một trong những cách mà Domain-Driven Design (DDD) có thể được khai thác nhằm giúp các hệ thống hoạt động độc lập là thông qua việc sử dụng Domain Event (sự kiện miền nghiệp vụ ghi lại điều có ý nghĩa đã xảy ra). Khi có điều gì đó quan trọng xảy ra trong một hệ thống, hệ thống đó sẽ phát sinh một Event tương ứng. Thường sẽ có nhiều Event như vậy diễn ra trong từng hệ thống, và bạn sẽ tạo ra một kiểu Event riêng biệt để ghi nhận từng sự kiện đó. Khi các Event phát sinh, chúng được công bố (publish) đến các bên quan tâm thông qua cơ chế gửi thông điệp. Đây chỉ là phần tóm lược bức tranh tổng thể. Trong trường hợp bạn đã bỏ qua các chi tiết của chủ đề này trong các chương trước, bạn nên xem lại kiến thức nền tảng từ Chương 4 (Architecture), Chương 8 (Domain Events), và Chương 10 (Aggregates) trước khi tiếp tục.

## Duy trì cập nhật thông tin về Product Owner và Team Member (Staying Informed about Product Owners and Team Members)

Agile Project Management Context cần quản lý danh sách các Scrum product owner và team member cho mỗi tenant (khách thuê hệ thống) đăng ký sử dụng dịch vụ. Tại bất kỳ thời điểm nào, một product owner đều có thể tạo một sản phẩm mới và sau đó phân công các thành viên vào nhóm. Làm thế nào để ứng dụng quản lý dự án Scrum biết được ai đang đảm nhận từng vai trò này? Câu trả lời là ứng dụng sẽ không tự thân gánh vác toàn bộ việc đó.

Thực tế, Agile Project Management Context sẽ để các vai trò đó được quản lý bởi Identity and Access Context — một lựa chọn hết sức tự nhiên và phù hợp. Trong hệ thống đó, mỗi tenant đăng ký dịch vụ Scrum sẽ có hai instance `Role` được tạo: `ScrumProductOwner` và `ScrumTeamMember`. Mỗi `User` cần đảm nhận một trong các vai trò đó sẽ được gán vào Role tương ứng. Dưới đây là phương thức Application Service trong Identity and Access Context chịu trách nhiệm gán một `User` vào một `Role`:

```java
package com.saasovation.identityaccess.application;
...

public class AccessService ... {
    ...
    @Transactional
    public void assignUserToRole(AssignUserToRoleCommand aCommand) {
        TenantId tenantId = new TenantId(aCommand.getTenantId());
        User user = this.userRepository
            .userWithUsername(
                tenantId,
                aCommand.getUsername());

        if (user != null) {
            Role role = this.roleRepository
                .roleNamed(
                    tenantId,
                    aCommand.getRoleName());

            if (role != null) {
                role.assignUser(user);
            }
        }
    }
    ...
}

```

Rất tốt, nhưng điều này giúp ích gì cho Agile Project Management Context trong việc xác định ai đang giữ vai trò `ScrumTeamMember` hay `ScrumProductOwner`? Cơ chế như sau: khi phương thức `assignUser()` của `Role` hoàn tất, nhiệm vụ cuối cùng của nó là phát hành một Event:

```java
package com.saasovation.identityaccess.domain.model.access;
...

public class Role extends Entity {
    ...
    public void assignUser(User aUser) {

```

```java
        if (aUser == null) {
            throw new NullPointerException("User must not be null.");
        }

        if (!this.tenantId().equals(aUser.tenantId())) {
            throw new IllegalArgumentException(
                "Wrong tenant for this user.");
        }

        this.group().addUser(aUser);

        DomainEventPublisher
            .instance()
            .publish(new UserAssignedToRole(
                this.tenantId(),
                this.name(),
                aUser.username(),
                aUser.person().name().firstName(),
                aUser.person().name().lastName(),
                aUser.person().emailAddress()));
    }
    ...
}

```

Event `UserAssignedToRole`, được bổ sung thêm thông tin về tên và địa chỉ email của `User`, cuối cùng sẽ được phân phối tới tất cả các bên quan tâm. Khi Agile Project Management Context nhận được Event này, nó sẽ dùng thông tin đó để đảm bảo một `TeamMember` hoặc `ProductOwner` mới được thiết lập trong mô hình của mình. Đây không phải là một use case quá phức tạp. Tuy nhiên, có nhiều chi tiết cần quản lý hơn những gì thoạt nhìn thấy. Hãy cùng phân tích kỹ các chi tiết này.

Thực tế cho thấy, việc lắng nghe thông báo từ RabbitMQ có nhiều khía cạnh có tính tái sử dụng rất cao. Chúng tôi đã có sẵn một thư viện hướng đối tượng đơn giản giúp việc dùng RabbitMQ Java client trở nên dễ dàng hơn. Giờ đây, chúng tôi sẽ thêm một lớp đơn giản nữa để giúp việc biến một lớp thành consumer (bên tiêu thụ thông điệp) của exchange queue trở nên cực kỳ thuận tiện:

```java
package com.saasovation.common.port.adapter.messaging.rabbitmq;
...

public abstract class ExchangeListener {
    private MessageConsumer messageConsumer;
    private Queue queue;

    public ExchangeListener() {
        super();
        this.attachToQueue();

```

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
        this.registerConsumer();
    }

    protected abstract String exchangeName();
    protected abstract void filteredDispatch(
        String aType,
        String aTextMessage);
    protected abstract String[] listensToEvents();

    protected String queueName() {
        return this.getClass().getSimpleName();
    }

    private void attachToQueue() {
        Exchange exchange = Exchange.fanOutInstance(
            ConnectionSettings.instance(),
            this.exchangeName(),
            true);

        this.queue = Queue.individualExchangeSubscriberInstance(
            exchange,
            this.exchangeName() + "." + this.queueName());
    }

    private Queue queue() {
        return this.queue;
    }

    private void registerConsumer() {
        this.messageConsumer = MessageConsumer.instance(this.queue(), false);
        this.messageConsumer.receiveOnly(
            this.listensToEvents(),
            new MessageListener(MessageListener.Type.TEXT) {
                @Override
                public void handleMessage(
                    String aType,
                    String aMessageId,
                    Date aTimestamp,
                    String aTextMessage,
                    long aDeliveryTag,
                    boolean isRedelivery) throws Exception {

                    filteredDispatch(aType, aTextMessage);
                }
            });
    }
}

```

`ExchangeListener` là một lớp cơ sở trừu tượng (abstract base class) mà các lớp con listener cụ thể có thể tái sử dụng. Một lớp con cụ thể chỉ cần bổ sung rất ít mã nguồn bên cạnh việc kế thừa lớp cơ sở này. Trước hết, nó chỉ cần đảm bảo constructor mặc định của lớp cơ sở được gọi — điều vốn dĩ luôn mặc định diễn ra. Sau đó, công việc còn lại chỉ là triển khai ba phương thức trừu tượng, trong đó có hai phương thức rất đơn giản: `exchangeName()`, `filteredDispatch()` và `listensToEvents()`.

Để triển khai `exchangeName()`, tất cả những gì cần làm là trả về chuỗi `String` chứa tên của exchange mà listener cụ thể này sẽ tiêu thụ thông báo. Để hiện thực hóa phương thức trừu tượng `listensToEvents()`, bạn phải trả về một mảng `String[]` chứa các kiểu thông báo mà bạn muốn tiếp nhận. Nhiều listener sẽ chỉ tiêu thụ duy nhất một loại thông báo, vì vậy chúng chỉ cần trả về một mảng có một phần tử duy nhất. Phương thức còn lại, `filteredDispatch()`, là phương thức phức tạp nhất trong ba phương thức vì nó chịu trách nhiệm thực thi các tác vụ nặng nhọc trong việc xử lý các thông điệp nhận được. Để hiểu rõ cách thức hoạt động, hãy xem listener xử lý các thông báo mang Event `UserAssignedToRole`:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...

public class TeamMemberEnablerListener extends ExchangeListener {
    @Autowired
    private TeamService teamService;

    public TeamMemberEnablerListener() {
        super();
    }

    @Override
    protected String exchangeName() {
        return Exchanges.IDENTITY_ACCESS_EXCHANGE_NAME;
    }

    @Override
    protected void filteredDispatch(
        String aType,
        String aTextMessage) {

        NotificationReader reader = new NotificationReader(aTextMessage);
        String roleName = reader.eventStringValue("roleName");

        if (!roleName.equals("ScrumProductOwner") && !roleName.equals("ScrumTeamMember")) {
            return;
        }

```

```java
        String emailAddress = reader.eventStringValue("emailAddress");
        String firstName = reader.eventStringValue("firstName");
        String lastName = reader.eventStringValue("lastName");
        String tenantId = reader.eventStringValue("tenantId.id");
        String username = reader.eventStringValue("username");
        Date occurredOn = reader.occurredOn();

        if (roleName.equals("ScrumProductOwner")) {
            this.teamService.enableProductOwner(
                new EnableProductOwnerCommand(
                    tenantId,
                    username,
                    firstName,
                    lastName,
                    emailAddress,
                    occurredOn));
        } else {
            this.teamService.enableTeamMember(
                new EnableTeamMemberCommand(
                    tenantId,
                    username,
                    firstName,
                    lastName,
                    emailAddress,
                    occurredOn));
        }
    }

    @Override
    protected String[] listensToEvents() {
        return new String[] {
            "com.saasovation.identityaccess.domain.model.access.UserAssignedToRole"
        };
    }
}

```

Constructor mặc định của `ExchangeListener` được gọi chính xác, `exchangeName()` trả về tên của exchange do Identity and Access Context công bố, và phương thức `listensToEvents()` trả về mảng gồm một phần tử chứa tên lớp đầy đủ (fully qualified class name) của Event `UserAssignedToRole`. Lưu ý rằng bên công bố và bên đăng ký nên cân nhắc việc sử dụng tên lớp đầy đủ, bao gồm cả tên Module lẫn tên lớp. Điều này giúp loại bỏ hoàn toàn các xung đột hoặc sự nhập nhằng tiềm ẩn có thể xảy ra giữa các Event có cùng tên hoặc tên tương tự đến từ các Bounded Context khác nhau.

Một lần nữa, chính `filteredDispatch()` mới là nơi chứa phần lớn hành vi xử lý. Phương thức này được đặt tên như vậy vì nó có thể tiếp tục lọc thông báo trước khi điều phối tới API của Application Service. Trong trường hợp này, nó thực sự lọc trước khi điều phối bằng cách bỏ qua tất cả các thông báo thuộc loại `UserAssignedToRole` không chứa Event về các vai trò có tên là `ScrumProductOwner` và `ScrumTeamMember`. Mặt khác, nếu các vai trò đó đúng là những vai trò chúng ta quan tâm nhận Event, chúng ta sẽ trích xuất thông tin chi tiết của `UserAssignedToRole` ra khỏi thông báo và điều phối tới Application Service có tên `TeamService`. Mỗi phương thức Service `enableProductOwner()` và `enableTeamMember()` đều nhận vào một command object (đối tượng lệnh), tương ứng là `EnableProductOwnerCommand` hoặc `EnableTeamMemberCommand`.

Ban đầu, có vẻ như một thành viên sẽ được tạo ra ngay sau khi nhận một trong những Event này. Tuy nhiên, vì mỗi `User` đều có khả năng được gán vào một trong các `Role` này, sau đó bị hủy gán rồi lại được gán lại, nên thành viên đại diện bởi `User` trong thông báo nhận được có thể đã tồn tại từ trước. Dưới đây là cách `TeamService` xử lý tình huống đó:

```java
package com.saasovation.agilepm.application;
...

public class TeamService ... {
    @Autowired
    private ProductOwnerRepository productOwnerRepository;
    @Autowired
    private TeamMemberRepository teamMemberRepository;
    ...
    @Transactional
    public void enableProductOwner(
        EnableProductOwnerCommand aCommand) {

        TenantId tenantId = new TenantId(aCommand.getTenantId());
        ProductOwner productOwner = this.productOwnerRepository.productOwnerOfIdentity(
            tenantId,
            aCommand.getUsername());

        if (productOwner != null) {
            productOwner.enable(aCommand.getOccurredOn());
        } else {
            productOwner = new ProductOwner(
                tenantId,
                aCommand.getUsername(),
                aCommand.getFirstName(),
                aCommand.getLastName(),
                aCommand.getEmailAddress(),
                aCommand.getOccurredOn());

```

```java
            this.productOwnerRepository.add(productOwner);
        }
    }
}

```

Ví dụ, phương thức Service `enableProductOwner()` xử lý khả năng `ProductOwner` cụ thể đó đã tồn tại. Nếu đối tượng đã tồn tại, chúng ta giả định rằng nó có thể cần được kích hoạt lại, do đó chúng ta điều phối tới thao tác lệnh tương ứng. Nếu `ProductOwner` chưa tồn tại, chúng ta khởi tạo một Aggregate mới và thêm nó vào Repository của nó. Trên thực tế, chúng ta xử lý `TeamMember` theo cách tương tự, vì vậy `enableTeamMember()` cũng được hiện thực hóa tương tự.

## Liệu bạn có gánh vác nổi trách nhiệm này? (Can You Handle the Responsibility?)

Mọi thứ dường như đều ổn thỏa và tốt đẹp. Quy trình trông khá đơn giản. Chúng ta có các kiểu Aggregate `ProductOwner` và `TeamMember`, và chúng ta đã thiết kế chúng sao cho mỗi đối tượng lưu giữ một số thông tin về `User` nền tảng từ Bounded Context bên ngoài. Nhưng bạn có nhận ra chúng ta vừa phải gánh vác bao nhiêu trách nhiệm khi thiết kế các Aggregate theo cách đó không?

Hãy nhớ lại rằng trong Collaboration Context, nhóm phát triển đã quyết định chỉ tạo các Value Object bất biến để lưu giữ các thông tin tương tự (xem phần 'Hiện thực hóa REST Client bằng Anticorruption Layer'). Vì các Value Object là bất biến nên nhóm sẽ không bao giờ phải bận tâm về việc giữ cho thông tin chia sẻ luôn được cập nhật. Dĩ nhiên, mặt trái của ưu điểm đó là nếu một số thông tin dùng chung bị thay đổi, Collaboration Context sẽ không bao giờ cập nhật các đối tượng liên quan mà nó đã tạo ra trong quá khứ. Vì thế, đội ngũ Agile Project Management đã chọn phương án đánh đổi ngược lại.

Tuy nhiên, giờ đây lại xuất hiện một số thách thức trong việc giữ cho các Aggregate luôn được cập nhật. Tại sao lại như vậy? Chẳng phải chúng ta chỉ cần lắng nghe thêm các thông báo mang Event phản ánh các thay đổi đối với các instance `User` tương ứng với các instance `ProductOwner` và `TeamMember` của chúng ta là xong sao? Đúng vậy, chúng ta hoàn toàn có thể và buộc phải làm điều đó. Nhưng thực tế là việc sử dụng hạ tầng gửi thông điệp khiến vấn đề này trở nên phức tạp hơn một chút so với vẻ bề ngoài.

Ví dụ, điều gì sẽ xảy ra nếu trong Identity and Access Context, một người quản lý lỡ tay hủy gán Joe Johnson khỏi vai trò `ScrumTeamMember`? Khi đó, chúng ta nhận được một thông báo mang Event cho biết sự kiện đó, và chúng ta dùng `TeamService` để vô hiệu hóa (disable) `TeamMember` tương ứng với Joe Johnson. Nhưng khoan đã. Vài giây sau, người quản lý nhận ra mình đã hủy gán nhầm người khỏi vai trò `ScrumTeamMember`, đáng lẽ người cần hủy gán phải là Joe Jones. Vì vậy, cô ấy nhanh chóng gán Joe Johnson trở lại vai trò đó và hủy gán Joe Jones. Tiếp theo, Agile Project Management Context nhận được các thông báo tương ứng, và mọi người đều hài lòng (ngoại trừ có lẽ là Joe Jones). Nhưng liệu mọi thứ có thực sự ổn thỏa không?

Chúng ta có thể đang đưa ra một giả định sai lầm về use case này. Chúng ta đang giả định rằng các thông báo sẽ được nhận theo đúng thứ tự mà chúng thực sự diễn ra trong Identity and Access Context. Tuy nhiên, mọi chuyện không phải lúc nào cũng suôn sẻ như vậy. Điều gì sẽ xảy ra nếu vì bất kỳ lý do gì, các thông báo về Joe Johnson lại được nhận theo thứ tự: `UserAssignedToRole` trước rồi mới đến `UserUnassignedFromRole`? Hậu quả là `TeamMember` tương ứng với Joe Johnson sẽ bị mắc kẹt ở trạng thái bị vô hiệu hóa (disabled), và trong trường hợp nhẹ nhất thì ai đó sẽ phải vá dữ liệu thủ công trong database của Agile PM, hoặc người quản lý sẽ phải dùng vài thủ thuật để kích hoạt lại đúng anh chàng Joe. Điều này hoàn toàn có thể xảy ra, và trớ trêu thay, dường như nó luôn xảy ra đúng vào lúc chúng ta chủ quan bỏ qua khả năng xảy ra của nó. Vậy làm thế nào để chúng ta ngăn chặn điều này?

Hãy xem xét kỹ hơn các command object mà chúng ta truyền làm tham số cho các API của `TeamService`. Ví dụ, hãy xem xét các lệnh `EnableTeamMemberCommand` và `DisableTeamMemberCommand`. Mỗi lệnh này đều yêu cầu phải cung cấp một đối tượng `Date`, cụ thể là `occurredOn`. Trên thực tế, tất cả các command object của chúng tôi đều được thiết kế theo cách này. Chúng tôi sẽ sử dụng các giá trị `occurredOn` để đảm bảo các Aggregate `ProductOwner` và `TeamMember` xử lý các thao tác lệnh một cách có nhận thức về thời gian (time-aware). Nhìn lại use case có thể gây rắc rối trước đó, hãy xem điều gì sẽ xảy ra nếu chúng ta xử lý tình huống `UserUnassignedFromRole` đến sau `UserAssignedToRole`, mặc dù chúng phát sinh theo thứ tự ngược lại:

```java
package com.saasovation.agilepm.application;
...

public class TeamService ... {
    ...
    @Transactional
    public void disableTeamMember(DisableTeamMemberCommand aCommand) {
        TenantId tenantId = new TenantId(aCommand.getTenantId());
        TeamMember teamMember = this.teamMemberRepository.teamMemberOfIdentity(
            tenantId,
            aCommand.getUsername());

        if (teamMember != null) {
            teamMember.disable(aCommand.getOccurredOn());
        }
    }
}

```

Lưu ý rằng khi điều phối tới phương thức lệnh `disable()` của `TeamMember`, chúng ta bắt buộc phải truyền giá trị `occurredOn` từ command object. Bản thân `TeamMember` sẽ sử dụng giá trị này trong nội bộ để đảm bảo rằng việc vô hiệu hóa chỉ diễn ra khi nó thực sự hợp lệ:

```java
package com.saasovation.agilepm.domain.model.team;
...

public abstract class Member extends Entity {
    ...
    private MemberChangeTracker changeTracker;
    ...
    public void disable(Date asOfDate) {
        if (this.changeTracker().canToggleEnabling(asOfDate)) {
            this.setEnabled(false);
            this.setChangeTracker(
                this.changeTracker().enablingOn(asOfDate));
        }
    }

    public void enable(Date asOfDate) {
        if (this.changeTracker().canToggleEnabling(asOfDate)) {
            this.setEnabled(true);
            this.setChangeTracker(
                this.changeTracker().enablingOn(asOfDate));
        }
    }
    ...
}

```

Lưu ý rằng hành vi Aggregate này được cung cấp bởi một lớp cơ sở trừu tượng dùng chung là `Member`. Cả hai phương thức `disable()` và `enable()` đều được thiết kế để truy vấn một `changeTracker` nhằm xác định xem thao tác được yêu cầu có thể được thực hiện hay không dựa trên tham số `asOfDate` (chính là giá trị `occurredOn` của lệnh). Value Object `MemberChangeTracker` lưu giữ thời điểm xảy ra của thao tác liên quan gần đây nhất và sử dụng thời điểm đó để trả lời câu truy vấn:

```java
package com.saasovation.agilepm.domain.model.team;
...

public final class MemberChangeTracker implements Serializable {
    private Date emailAddressChangedOn;
    private Date enablingOn;
    private Date nameChangedOn;
    ...
    public boolean canToggleEnabling(Date asOfDate) {
        return this.enablingOn().before(asOfDate);
    }
    ...

```

```java
    public MemberChangeTracker enablingOn(Date asOfDate) {
        return new MemberChangeTracker(
            asOfDate,
            this.nameChangedOn(),
            this.emailAddressChangedOn());
    }
    ...
}

```

Nếu thao tác được cho phép và được thực thi, một instance `MemberChangeTracker` thay thế sẽ được lấy thông qua phương thức `enablingOn()` tương ứng. Vì chúng ta có thể dự liệu rằng các thay đổi `PersonNameChanged` và `PersonContactInformationChanged` có thể đến sai thứ tự, nên các cơ chế tương tự cũng được cung cấp thông qua `emailAddressChangedOn` và `nameChangedOn`. Trên thực tế, có thêm một bước kiểm tra bổ sung đối với trường hợp thay đổi địa chỉ email: có thể các Event `PersonContactInformationChanged` chỉ nhằm thông báo về việc đổi số điện thoại hoặc địa chỉ bưu điện chứ không phải là thay đổi địa chỉ email (vốn ít xảy ra hơn):

```java
package com.saasovation.agilepm.domain.model.team;
...

public abstract class Member extends Entity {
    ...
    public void changeEmailAddress(
        String anEmailAddress,
        Date asOfDate) {

        if (this.changeTracker().canChangeEmailAddress(asOfDate)
            && !this.emailAddress().equals(anEmailAddress)) {

            this.setEmailAddress(anEmailAddress);
            this.setChangeTracker(
                this.changeTracker().emailAddressChangedOn(asOfDate));
        }
    }
    ...
}

```

Ở đây chúng ta kiểm tra xem trên thực tế địa chỉ email có thực sự thay đổi hay không. Nếu không đổi, chúng ta không muốn ghi nhận nó là đã thay đổi. Nếu chúng ta ghi nhận, thì một Event đến sai thứ tự thuộc cùng loại nhưng thực sự chứa địa chỉ email đã đổi sau đó sẽ bị bỏ qua mất.

`MemberChangeTracker` còn đóng vai trò giúp cho các thao tác lệnh trên các lớp con của `Member` đạt được tính Idempotent (tính lũy đẳng - thực thi nhiều lần cho ra cùng một kết quả như thực thi một lần duy nhất), nhờ đó khi cùng một thông báo được hạ tầng gửi thông điệp chuyển giao nhiều lần, các thông báo phân phối thừa thãi sẽ bị loại bỏ.

Chúng ta có thể phản biện rằng việc đưa `MemberChangeTracker` vào thiết kế Aggregate là một sai lầm, và kết luận rằng điều này chẳng liên quan gì đến Ubiquitous Language của các nhóm làm việc theo Scrum. Điều đó đúng. Tuy nhiên, chúng ta không bao giờ để lộ `MemberChangeTracker` ra bên ngoài ranh giới của Aggregate. Nó hoàn toàn là một chi tiết triển khai kỹ thuật, và các client sẽ không bao giờ biết đến sự tồn tại của nó. Chi tiết duy nhất mà client nhận biết được là họ phải cung cấp giá trị `occurredOn` ghi nhận thời điểm mà sự kiện sửa đổi tương ứng thực sự diễn ra. Hơn nữa, đây chính xác là loại chi tiết kỹ thuật mà Pat Helland đã khuyến nghị khi ông mô tả cách quản lý các mối quan hệ đối tác (partner relationships) trong tài liệu nghiên cứu về các hệ thống phân tán, có khả năng mở rộng và đạt tính nhất quán sau cùng (eventual consistency). Trong bài báo đó [Helland], hãy xem cụ thể mục 5, "Activities: Coping with Messy Messages" (Các hoạt động: Đối phó với các thông điệp lộn xộn).

Bây giờ, hãy quay trở lại với việc giải quyết các trách nhiệm mới của chúng ta . . .

Mặc dù đây chỉ là một ví dụ rất cơ bản về việc duy trì các thay đổi đối với thông tin trùng lặp bắt nguồn từ một Bounded Context ngoại lai, nhưng đây không phải là một trách nhiệm đơn giản, ít nhất là khi bạn đang sử dụng một cơ chế gửi thông điệp có khả năng phân phối thông điệp sai thứ tự và lặp lại nhiều lần. 1 Hơn nữa, khi nhận thức được tất cả các thao tác có thể xảy ra trong Identity and Access Context gây ảnh hưởng tới chỉ một vài thuộc tính mà chúng ta duy trì trong `Member`, đó thực sự là một hồi chuông cảnh tỉnh:

* PersonContactInformationChanged
* PersonNameChanged
* UserAssignedToRole
* UserUnassignedFromRole

Và sau đó chúng ta nhận ra rằng còn có một vài Event khác cũng quan trọng không kém cần phải phản ứng:

* UserEnablementChanged
* TenantActivated
* TenantDeactivated

Những thực tế này nhấn mạnh rằng, nếu có thể, tốt nhất hãy giảm thiểu hoặc thậm chí loại bỏ hoàn toàn việc nhân bản trùng lặp thông tin giữa các Bounded Context. Việc tránh hoàn toàn sự trùng lặp thông tin có thể là bất khả thi. Các thỏa thuận mức dịch vụ (SLA) có thể khiến việc truy xuất dữ liệu từ xa mỗi khi cần trở nên phi thực tế. Đó là một trong những động lực khiến nhóm phát triển quyết định lưu trữ tên cá nhân và địa chỉ email của `User` tại bộ nhớ cục bộ. Tuy nhiên, việc đặt mục tiêu giảm lượng thông tin ngoại lai mà chúng ta phải chịu trách nhiệm sẽ giúp công việc của chúng ta dễ dàng hơn rất nhiều. Đó là tư duy tích hợp theo chủ nghĩa tối giản (minimalist's mindset).

---

1. Đây có thể là trường hợp mà việc áp dụng phương pháp tiếp cận RESTful để tiêu thụ thông báo mang lại lợi thế rõ rệt, vì các thông báo được đảm bảo phân phối theo đúng thứ tự mà chúng được ghi nối tiếp vào Event Store (kho lưu trữ sự kiện) (Chương 4, Phụ lục A). Các thông báo, từ đầu tiên đến cuối cùng, có thể được tiêu thụ lặp đi lặp lại vì nhiều lý do khác nhau mà vẫn luôn đảm bảo đúng thứ tự mỗi lần.

Dĩ nhiên, không có cách nào tránh khỏi việc trùng lặp định danh tenant và định danh user, và nhìn chung việc chia sẻ định danh giữa các Bounded Context là điều cần thiết. Đó là một trong những phương thức chủ đạo để các Bounded Context có thể tích hợp với nhau. Hơn nữa, định danh hoàn toàn an toàn để chia sẻ vì nó mang tính bất biến. Chúng ta thậm chí có thể sử dụng cơ chế vô hiệu hóa Aggregate và xóa mềm (soft deletion) để đảm bảo các đối tượng được tham chiếu không bao giờ biến mất hoàn toàn, như cách chúng ta thực hiện với `Tenant`, `User`, `ProductOwner` và `TeamMember`.

Lời nhắc nhở này không có nghĩa là các Domain Event không nên được làm giàu (enriched) bằng các thuộc tính truyền tải thông tin. Chắc chắn rằng Event phải cung cấp đầy đủ thông tin để thông báo cho bên tiêu thụ biết họ cần thực hiện các bước xử lý nào nhằm phản ứng lại những dữ kiện đã diễn ra trong quá khứ. Dù vậy, dữ liệu của Event hoàn toàn có thể được dùng để thực hiện các phép tính toán và suy luận trạng thái tại Bounded Context ngoại lai tiếp nhận mà không nhất thiết phải lưu giữ và gánh vác trách nhiệm đồng bộ hóa nó với trạng thái chính thức nằm tại system of record (hệ thống nguồn dữ liệu chuẩn).

## Các tiến trình chạy dài và cách thoái thác trách nhiệm (Long-Running Processes, and Avoiding Responsibility)

Nếu chúng ta ví những gì vừa mô tả trong phần trước giống như một người trưởng thành đầy trách nhiệm, thì có thể so sánh phần này với nỗ lực muốn quay trở lại thời niên thiếu của chúng ta. Bạn biết đấy, người lớn phải gánh vác đủ mọi loại trách nhiệm: cha mẹ phải mua xe hơi, mua bảo hiểm cho xe, chi tiền đổ xăng vào bình và trả tiền sửa chữa xe. Thời niên thiếu, chúng ta chỉ muốn lấy xe của bố mẹ đi chơi mà không muốn phải trả bất kỳ chi phí nào cho chiếc xe đó. Chẳng có thiếu niên nào lại đi trả tiền mua xe trả góp cho cha mẹ, tự bỏ tiền túi đổ xăng, trả tiền cho thợ sửa xe hay gánh chi phí bảo hiểm. Họ chỉ muốn mặc cho cha mẹ lo liệu cái thứ "trách nhiệm" kinh khủng bắt đầu bằng chữ T (R-word) đó, để bản thân có thể thoải mái vui chơi.

> 💡 **Giải thích thêm:** Tác giả sử dụng phép ẩn dụ văn hóa thường ngày: người lớn phải cáng đáng mọi chi phí và rủi ro ("R-word" trong tiếng Anh là lối nói châm biếm chỉ từ "Responsibility" - Trách nhiệm, bắt chước cách nói tránh các từ cấm kỵ như "F-word"), còn tuổi thiếu niên chỉ muốn tận hưởng tiện ích mà không muốn vướng bận trách nhiệm. Trong kiến trúc phần mềm, khi một Bounded Context nhân bản dữ liệu từ Context khác, nó buộc phải gánh vác gánh nặng kỹ thuật phức tạp để duy trì tính nhất quán. Bằng cách áp dụng Long-Running Process (tiến trình nghiệp vụ bất đồng bộ kéo dài nhiều bước, tương tự mô hình Saga), nhóm kiến trúc đã "đá quả bóng trách nhiệm" sang Context nguồn (system of record), để hệ thống nguồn tự chịu trách nhiệm lưu trữ và bảo trì dữ liệu của chính nó.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Những gì chúng ta đang làm trong phần này là thỏa sức ứng dụng các Long-Running Process (tiến trình xử lý kéo dài) (4), nhưng kiên quyết từ chối tiếp nhận bất kỳ trách nhiệm nặng nề nào phát sinh khi nhân bản thông tin từ các Bounded Context khác. Chúng ta sẽ để cho system of record tự giải quyết thông tin của chính nó, sau khi chúng ta đã tận hưởng trọn vẹn việc bắt Bounded Context ngoại lai đó tạo và duy trì dữ liệu phục vụ cho chúng ta.

Trong Chương 3: Context Maps, chúng ta đã được giới thiệu về use case Tạo Sản Phẩm (Create a Product):

Tiền điều kiện: Tính năng cộng tác đã được kích hoạt (tùy chọn đã được mua bản quyền).

1. Người dùng cung cấp thông tin mô tả Sản phẩm (Product).
2. Người dùng biểu thị mong muốn tạo một cuộc thảo luận nhóm.

3. Người dùng yêu cầu tạo Sản phẩm đã định nghĩa.
4. Hệ thống tạo Sản phẩm đi kèm một Diễn đàn (Forum) và Cuộc thảo luận (Discussion).

Đây là nơi niềm vui bắt đầu, và cũng là nơi chúng ta "đá quả bóng trách nhiệm" qua đường truyền mạng.

Trong Chương 3 (Context Maps), nhóm phát triển đã đề xuất sử dụng giải pháp tiếp cận RESTful để tích hợp giữa hai Bounded Context này. Tuy nhiên, cuối cùng nhóm đã quyết định chọn giải pháp dựa trên thông điệp.

Ngoài ra, một trong những điều đầu tiên bạn có thể nhận thấy là khái niệm ban đầu được thêm vào Ubiquitous Language với tên gọi `Discussion` (trong Chương 3) đã được tinh chỉnh lại. Nhóm Agile Project Management nhận thấy cần phải phân biệt giữa các loại thảo luận khác nhau, do đó hiện có hai loại khác nhau: `ProductDiscussion` và `BacklogItemDiscussion`. (Trong phần này chúng ta chỉ quan tâm đến `ProductDiscussion`.) Cả hai Value Object này đều có trạng thái và hành vi cơ bản giống nhau, nhưng sự phân biệt này mang lại tính an toàn kiểu (type safety) giúp lập trình viên tránh việc gắn nhầm thảo luận vào `Product` và `BacklogItem`. Xét trên mọi khía cạnh thực tế, chúng hoàn toàn tương đồng. Mỗi kiểu thảo luận này chỉ lưu giữ trạng thái khả dụng của nó và — nếu một cuộc thảo luận đã được thiết lập — thì lưu giữ thêm định danh của instance Aggregate `Discussion` thực sự bên trong Collaboration Context.

Cần khẳng định rằng đề xuất ban đầu trong Agile Project Management Context về việc đặt tên một Value Object trùng với tên Aggregate trong Collaboration Context không phải là một sai lầm trong nhận định. Do đó, để hoàn toàn rõ ràng: tên của Value Object không phải bị đổi từ `Discussion` thành `ProductDiscussion` nhằm phân biệt nó với Aggregate trong Collaboration Context. Đứng trên góc độ của Context Mapping, việc giữ nguyên tên của Value Object hoàn toàn không có vấn đề gì, bởi chính Context đã làm nhiệm vụ phân biệt hai đối tượng này. Quyết định tạo ra hai kiểu Value Object riêng biệt trong Agile Project Management Context chỉ xuất phát thuần túy từ các yêu cầu nội tại của mô hình miền cục bộ biệt lập.

Để đi sâu vào chi tiết, trước tiên chúng ta hãy xem xét Application Service (API) được sử dụng để tạo một `Product`:

```java
package com.saasovation.agilepm.application;
...

public class ProductService ... {
    @Autowired
    private ProductRepository productRepository;
    @Autowired
    private ProductOwnerRepository productOwnerRepository;
    ...

```

```java
    @Transactional
    public String newProductWithDiscussion(
        NewProductCommand aCommand) {

        return this.newProductWith(
            aCommand.getTenantId(),
            aCommand.getProductOwnerId(),
            aCommand.getName(),
            aCommand.getDescription(),
            this.requestDiscussionIfAvailable());
    }
    ...
}

```

Thực tế có hai cách để tạo một `Product` mới. Phương thức thứ nhất, không hiển thị ở đây, sẽ tạo một `Product` không có `Discussion`, trong khi phương thức hiển thị ở đây sẽ cố gắng khiến một `ProductDiscussion` cuối cùng được tạo và gắn vào `Product`. Hai phương thức nội bộ là `newProductWith()` và `requestDiscussionIfAvailable()` không được trình bày ở đây. Phương thức thứ hai được dùng để kiểm tra xem add-on CollabOvation có được kích hoạt hay không. Nếu có, trạng thái khả dụng `REQUESTED` sẽ được trả về; ngược lại, giá trị trạng thái trả về là `ADD_ON_NOT_ENABLED`. Phương thức `newProductWith()` sẽ gọi constructor của `Product`, vì vậy tiếp theo chúng ta hãy cùng xem constructor này:

```java
package com.saasovation.agilepm.domain.model.product;
...

public class Product extends ConcurrencySafeEntity {
    ...
    public Product(
        TenantId aTenantId,
        ProductId aProductId,
        ProductOwnerId aProductOwnerId,
        String aName,
        String aDescription,
        DiscussionAvailability aDiscussionAvailability) {

        this();
        this.setTenantId(aTenantId);
        this.setProductId(aProductId);
        this.setProductOwnerId(aProductOwnerId);
        this.setName(aName);
        this.setDescription(aDescription);
        this.setDiscussion(
            ProductDiscussion.fromAvailability(
                aDiscussionAvailability));

```

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
        DomainEventPublisher
            .instance()
            .publish(new ProductCreated(
                this.tenantId(),
                this.productId(),
                this.productOwnerId(),
                this.name(),
                this.description(),
                this.discussion().availability().isRequested()));
    }
    ...
}

```

Client bắt buộc phải truyền vào một `DiscussionAvailability`, mang một trong các trạng thái sau: `ADD_ON_NOT_ENABLED`, `NOT_REQUESTED`, hoặc `REQUESTED`. Trạng thái `READY` được dành riêng làm trạng thái hoàn tất. Bất kỳ trạng thái nào trong hai trạng thái đầu tiên đều dẫn đến việc tạo ra một `ProductDiscussion` mang đúng trạng thái đó, nghĩa là sẽ không có cuộc thảo luận liên kết nào được tạo kèm theo, ít nhất là không bắt nguồn từ việc gọi constructor. Khi nhận được yêu cầu với trạng thái thứ ba, `REQUESTED`, `ProductDiscussion` sẽ được tạo với trạng thái `PENDING_SETUP`. Dưới đây là Factory Method của `ProductDiscussion` được sử dụng bởi constructor của `Product`:

```java
package com.saasovation.agilepm.domain.model.product;
...

public final class ProductDiscussion implements Serializable {
    ...
    public static ProductDiscussion fromAvailability(
        DiscussionAvailability anAvailability) {

        if (anAvailability.isReady()) {
            throw new IllegalArgumentException(
                "Cannot be created ready.");
        }

        DiscussionDescriptor descriptor = new DiscussionDescriptor(
            DiscussionDescriptor.UNDEFINED_ID);

        return new ProductDiscussion(descriptor, anAvailability);
    }
    ...
}

```

Miễn là yêu cầu không phải là trạng thái `READY` (vì điều đó sẽ gây ra lỗi), chúng ta sẽ nhận được một `ProductDiscussion` với một trong ba trạng thái còn lại cùng một descriptor chưa xác định (undefined descriptor). Nếu trạng thái là `REQUESTED`, một Long-Running Process sẽ quản lý việc khởi tạo cuộc thảo luận cộng tác và sau đó thiết lập liên kết của nó với `Product`. Cơ chế ra sao? Hãy nhớ lại rằng hành động cuối cùng mà constructor của `Product` thực hiện là phát hành Event `ProductCreated`:

```java
package com.saasovation.agilepm.domain.model.product;
...

public Product(...) {
    ...
    DomainEventPublisher
        .instance()
        .publish(new ProductCreated(
            this.tenantId(),
            this.productId(),
            this.productOwnerId(),
            this.name(),
            this.description(),
            this.discussion().availability().isRequested()));
}
...
}

```

Nếu trạng thái khả dụng của thảo luận là `REQUESTED`, tham số cuối cùng truyền vào constructor của Event sẽ là `true` — đây chính xác là điều kiện cần thiết để kích hoạt Long-Running Process.

Hãy nhớ lại Chương 8 (Domain Events): từng instance Event đơn lẻ, bao gồm cả các Event kiểu `ProductCreated`, đều được ghi nối tiếp vào một Event Store dành riêng cho Bounded Context nơi Event đó phát sinh. Tất cả các Event mới được ghi vào sau đó sẽ được chuyển tiếp từ Event Store đến các bên quan tâm thông qua cơ chế gửi thông điệp. Trong trường hợp của SaaSOvation, các nhóm đã quyết định chọn RabbitMQ cho mục đích này. Chúng ta cần xây dựng một Long-Running Process đơn giản để quản lý việc tạo thảo luận và sau đó gắn nó vào `Product`.

Trước khi đi sâu vào chi tiết của Long-Running Process, hãy cùng xem xét thêm một trường hợp khác có thể dẫn đến việc yêu cầu thảo luận. Điều gì sẽ xảy ra nếu khi một instance `Product` được tạo lần đầu, cuộc thảo luận chưa được yêu cầu, hoặc add-on cộng tác chỉ mới vừa được kích hoạt sau đó? Sau này, product owner quyết định bổ sung cuộc thảo luận và lúc này add-on đã sẵn sàng. Khi đó, product owner có thể sử dụng phương thức lệnh sau trên `Product`:

```java
package com.saasovation.agilepm.domain.model.product;
...

public class Product extends ConcurrencySafeEntity {
    ...
    public void requestDiscussion(
        DiscussionAvailability aDiscussionAvailability) {

```

```java
        if (!this.discussion().availability().isReady()) {
            this.setDiscussion(
                ProductDiscussion.fromAvailability(
                    aDiscussionAvailability));

            DomainEventPublisher
                .instance()
                .publish(new ProductDiscussionRequested(
                    this.tenantId(),
                    this.productId(),
                    this.productOwnerId(),
                    this.name(),
                    this.description(),
                    this.discussion().availability().isRequested()));
        }
    }
    ...
}

```

Phương thức `requestDiscussion()` nhận tham số quen thuộc `DiscussionAvailability`, bởi client phải chứng minh cho `Product` thấy rằng add-on cộng tác đã được bật. Dĩ nhiên, client có thể "gian lận" tại đây và luôn truyền vào `REQUESTED`, nhưng điều đó cuối cùng sẽ dẫn đến một lỗi bế tắc nếu add-on thực sự không khả dụng. Tại đây cũng vậy, nếu trạng thái khả dụng của thảo luận là `REQUESTED`, tham số cuối cùng truyền vào constructor của Event sẽ mang giá trị `true`, đúng chuẩn điều kiện cần thiết để khởi chạy Long-Running Process:

```java
package com.saasovation.agilepm.domain.model.product;
...

public class ProductDiscussionRequested implements DomainEvent {
    ...
    public ProductDiscussionRequested(
        TenantId aTenantId,
        ProductId aProductId,
        ProductOwnerId aProductOwnerId,
        String aName,
        String aDescription,
        boolean isRequestingDiscussion) {
        ...
    }
    ...
}

```

Event này có các thuộc tính hoàn toàn trùng khớp với `ProductCreated`, điều này cho phép cả hai kiểu Event đều có thể được xử lý bởi cùng một listener.

Chúng ta có thể đặt câu hỏi: liệu việc phát hành Event này có ý nghĩa gì không nếu trạng thái khả dụng không phải là `REQUESTED`? Việc này hoàn toàn có ý nghĩa, bởi vì bất kể yêu cầu có thể được đáp ứng hay không thì yêu cầu đó trên thực tế vẫn đã được đưa ra, trừ khi nó hiện đang ở trạng thái `READY`. Trách nhiệm xác định xem có nên thực sự hành động đáp lại Event hay không thuộc về các listener. Có thể việc nhận được Event này với `isRequestingDiscussion` đặt thành `false` phản ánh một vấn đề bất thường, hoặc quá trình cài đặt add-on đang diễn ra nhưng chưa hoàn tất. Do đó, có thể cần đến sự can thiệp thủ công — ví dụ tiến trình có thể cần gửi một email cảnh báo tới nhóm quản trị viên.

Các lớp được sử dụng để quản lý Long-Running Process ở phía Agile Project Management Context tương tự như các lớp dùng để quản lý việc tạo và bảo trì các Aggregate `ProductOwner` và `TeamMember` (xem phần trước). Mỗi listener được giới thiệu ở đây đều được cấu hình bằng Spring để nó tự động được khởi tạo khi Spring Application Context được tạo cho Bounded Context này. Listener đầu tiên đăng ký nhận hai loại thông báo trên `AGILEPM_EXCHANGE_NAME`, gồm `ProductCreated` và `ProductDiscussionRequested`:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...

public class ProductDiscussionRequestedListener extends ExchangeListener {
    ...
    @Override
    protected String exchangeName() {
        return Exchanges.AGILEPM_EXCHANGE_NAME;
    }
    ...
    @Override
    protected String[] listensToEvents() {
        return new String[] {
            "com.saasovation.agilepm.domain.model.product.ProductCreated",
            "com.saasovation.agilepm.domain.model.product.ProductDiscussionRequested"
        };
    }
    ...
}

```

`COLLABORATION_EXCHANGE_NAME` là mối quan tâm của listener thứ hai, cụ thể là dành cho thông báo `DiscussionStarted`:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...

public class DiscussionStartedListener extends ExchangeListener {
    ...

```

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
    @Override
    protected String exchangeName() {
        return Exchanges.COLLABORATION_EXCHANGE_NAME;
    }
    ...
    @Override
    protected String[] listensToEvents() {
        return new String[] {
            "com.saasovation.collaboration.domain.model.forum.DiscussionStarted"
        };
    }
    ...
}

```

Bạn có thể dễ dàng đoán được diễn biến tiếp theo. Nếu listener đầu tiên nhận được `ProductCreated` hoặc `ProductDiscussionRequested`, nó sẽ gửi một command sang Collaboration Context yêu cầu tạo một `Forum` và `Discussion` mới thay mặt cho `Product`. Khi yêu cầu đó được các thành phần trong Collaboration Context hoàn tất, thông báo `DiscussionStarted` sẽ được công bố và một khi nhận được thông báo này, định danh cuộc thảo luận tương ứng sẽ được khởi tạo và gán vào `Product`. Tóm lại, toàn bộ Long-Running Process này diễn ra như vậy. Dưới đây là cách `filteredDispatch()` hoạt động trong listener đầu tiên:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...

public class ProductDiscussionRequestedListener extends ExchangeListener {
    private static final String COMMAND =
        "com.saasovation.collaboration.discussion.CreateExclusiveDiscussion";
    ...
    @Override
    protected void filteredDispatch(
        String aType,
        String aTextMessage) {

        NotificationReader reader = new NotificationReader(aTextMessage);

        if (!reader.eventBooleanValue("requestingDiscussion")) {
            return;
        }

        Properties parameters = this.parametersFrom(reader);
        PropertiesSerializer serializer = PropertiesSerializer.instance();
        String serialization = serializer.serialize(parameters);
        String commandId = this.commandIdFrom(parameters);

```

```java
        this.messageProducer()
            .send(
                serialization,
                MessageParameters.durableTextParameters(
                    COMMAND,
                    commandId,
                    new Date()))
            .close();
    }
    ...
}

```

Đối với cả hai kiểu Event là `ProductCreated` hay `ProductDiscussionRequested`, nếu thuộc tính `requestingDiscussion` mang giá trị `false`, chúng ta sẽ bỏ qua Event. Ngược lại, chúng ta sẽ xây dựng một command `CreateExclusiveDiscussion` từ trạng thái của Event và gửi command đó tới message exchange của Collaboration Context.

Đây là thời điểm thích hợp để tạm dừng và suy ngẫm về cách tiến trình này được thiết kế. Liệu Agile Project Management Context có thực sự nên thiết lập một listener để lắng nghe một Event do chính Aggregate cục bộ của nó phát hành hay không? Liệu có tốt hơn nếu tạo một listener lắng nghe Event `ProductCreated` ngay bên trong Collaboration Context? Nếu làm như vậy, chúng ta chỉ cần để listener trong Collaboration Context quản lý việc tạo `Forum` và `Discussion` độc quyền, đồng thời cắt giảm được một phần mã nguồn trong Agile Project Management Context. Việc xác định xem cách tiếp cận nào tốt hơn đòi hỏi chúng ta phải cân nhắc một số yếu tố.

Liệu việc một Bounded Context thượng nguồn (upstream) lại đi lắng nghe các Event do một Context hạ nguồn (downstream) phát hành có hợp lý không? Hoặc giả, trong một Event-Driven Architecture (kiến trúc hướng sự kiện) (4), các hệ thống có thực sự bị phân định rạch ròi theo quan hệ upstream và downstream hay không? Liệu chúng có nhất thiết phải bị đóng khung vào khuôn mẫu đó? Có lẽ yếu tố quan trọng hơn cần xem xét là: liệu có đúng đắn không khi một Event `ProductCreated` lại được diễn giải bên trong Collaboration Context như một chỉ thị báo hiệu rằng một `Forum` và `Discussion` độc quyền cần phải được tạo ra? Trên thực tế, liệu `ProductCreated` có mang bất kỳ ý nghĩa nghiệp vụ nào đối với Collaboration Context hay không? Sẽ có thêm bao nhiêu Context khác trong tương lai cũng muốn nhận được sự hỗ trợ tự động tương tự cho chính tính năng này dựa trên các kiểu Event đặc thù của riêng họ? Liệu có nên đặt gánh nặng phải hỗ trợ vô số Event ngoại lai dưới dạng các lệnh khởi tạo lên vai Collaboration Context hay không? Tuy nhiên, vẫn còn một yếu tố khác cần xem xét, đòi hỏi chúng ta phải quản lý sự thành công của các Long-Running Process một cách cẩn trọng hơn. Chủ đề này, được thảo luận ngay sau đây, có thể sẽ giúp làm sáng tỏ lý do tại sao chúng tôi lại tiếp cận theo cách thức cụ thể này.

Bây giờ, hãy quay trở lại với ví dụ . . . Sau khi được tiếp nhận trong Collaboration Context, command sẽ được điều chỉnh để chuyển tiếp tới `ForumService`, một Application Service. Lưu ý rằng API này chưa được thiết kế để sử dụng các tham số dạng command mà vẫn nhận các tham số thuộc tính riêng lẻ: