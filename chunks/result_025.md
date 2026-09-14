![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000542_cb54814c38ab5233fe33f16971a406f3e6e012889ccc601fe7fedbb6cfcbd80c.png)

```java
package com.saasovation.collaboration.infrastructure.messaging;
...
public class ExclusiveDiscussionCreationListener extends ExchangeListener {
    @Autowired
    private ForumService forumService;
    ...
    @Override
    protected void filteredDispatch(
            String aType,
            String aTextMessage) {
        NotificationReader reader = new NotificationReader(aTextMessage);
        String tenantId = reader.eventStringValue("tenantId");
        String exclusiveOwnerId = reader.eventStringValue("exclusiveOwnerId");
        String forumSubject = reader.eventStringValue("forumTitle");
        String forumDescription = reader.eventStringValue("forumDescription");
        String discussionSubject = reader.eventStringValue("discussionSubject");
        String creatorId = reader.eventStringValue("creatorId");
        String moderatorId = reader.eventStringValue("moderatorId");

        forumService.startExclusiveForumWithDiscussion(
                tenantId,
                creatorId,
                moderatorId,
                forumSubject,
                forumDescription,
                discussionSubject,
                exclusiveOwnerId);
    }
    ...
}

```

Điều đó nghe rất hợp lý, nhưng chẳng phải `ExclusiveDiscussionCreationListener` này nên gửi một thông điệp phản hồi ngược lại cho Agile Project Management Context (Bounded Context - ngữ cảnh giới hạn quản lý dự án Agile) hay sao? Ồ, không hẳn vậy. Cả hai Aggregate (cụm đối tượng / khối gộp các thực thể và giá trị) `Forum` và `Discussion` đều phát ra một Event (sự kiện) để phản hồi lại việc khởi tạo tương ứng của chúng: `ForumStarted` và `DiscussionStarted`. Bounded Context này xuất bản tất cả các Domain Event (sự kiện miền) của nó thông qua exchange (bộ định tuyến / điểm trao đổi thông điệp trong kiến trúc messaging), được xác định bởi `COLLABORATION_EXCHANGE_NAME`. Đó là lý do tại sao `DiscussionStartedListener` trong Agile Project Management Context nhận được sự kiện `DiscussionStarted`. Và dưới đây là những gì listener (bộ lắng nghe sự kiện) này thực hiện khi nhận được sự kiện:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...
public class DiscussionStartedListener extends ExchangeListener {
    @Autowired
    private ProductService productService;
    ...
    @Override
    protected void filteredDispatch(
            String aType,
            String aTextMessage) {
        NotificationReader reader = new NotificationReader(aTextMessage);
        String tenantId = reader.eventStringValue("tenant.id");
        String productId = reader.eventStringValue("exclusiveOwner");
        String discussionId = reader.eventStringValue("discussionId.id");

        productService.initiateDiscussion(
                new InitiateDiscussionCommand(
                        tenantId,
                        productId,
                        discussionId));
    }
    ...
}

```

Listener này chuyển đổi các thuộc tính Event từ thông báo nhận được để truyền đi dưới dạng một command (lệnh thao tác) tới Application Service (dịch vụ tầng ứng dụng) `ProductService`. Phương thức dịch vụ `initiateDiscussion()` này hoạt động như sau:

```java
package com.saasovation.agilepm.application;
...
public class ProductService ... {
    @Autowired
    private ProductRepository productRepository;
    ...
    @Transactional
    public void initiateDiscussion(
            InitiateDiscussionCommand aCommand) {
        Product product = productRepository
                .productOfId(
                        new TenantId(aCommand.getTenantId()),
                        new ProductId(aCommand.getProductId()));

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000543_be9c11ba540e1a6947d4b8fec26e9d47359160d3daad55460ebd9772a2ebe1c5.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000544_172148f205c2df89b7c7d09ecfa39454fed8753fc21d1743a981fcab9a1f3d38.png)

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
        if (product == null) {
            throw new IllegalStateException(
                    "Unknown product of tenant id: "
                    + aCommand.getTenantId()
                    + " and product id: "
                    + aCommand.getProductId());
        }
        product.initiateDiscussion(
                new DiscussionDescriptor(
                        aCommand.getDiscussionId()));
    }
    ...
}

```

Cuối cùng, hành vi `initiateDiscussion()` của Aggregate `Product` được thực thi:

```java
package com.saasovation.agilepm.domain.model.product;
...
public class Product extends ConcurrencySafeEntity {
    ...
    public void initiateDiscussion(DiscussionDescriptor aDescriptor) {
        if (aDescriptor == null) {
            throw new IllegalArgumentException(
                    "The descriptor must not be null.");
        }
        if (this.discussion().availability().isRequested()) {
            this.setDiscussion(this.discussion()
                    .nowReady(aDescriptor));
            DomainEventPublisher
                    .instance()
                    .publish(new ProductDiscussionInitiated(
                            this.tenantId(),
                            this.productId(),
                            this.discussion()));
        }
    }
    ...
}

```

Nếu thuộc tính `discussion` của `Product` vẫn đang ở trạng thái `REQUESTED`, nó sẽ được chuyển đổi sang trạng thái `READY` cùng với `DiscussionDescriptor` (đối tượng mô tả cuộc thảo luận), mang tham chiếu định danh đến `Discussion` độc quyền trong Collaboration Context (Bounded Context cộng tác). Yêu cầu tạo `Forum` và `Discussion` dành riêng và liên kết với `Product` khi đó vừa đạt được trạng thái nhất quán, mặc dù điều này diễn ra theo mô hình eventual consistency (tính nhất quán cuối cùng).

Tuy nhiên, nếu tại thời điểm gọi lệnh này mà `discussion` đã ở trạng thái `READY`, nó sẽ không chuyển đổi trạng thái thêm nữa. Đây có phải là lỗi không? Không. Đó là một cách để đảm bảo rằng `initiateDiscussion()` là một thao tác idempotent (thao tác có tính lũy đẳng - thực thi nhiều lần vẫn cho kết quả như một lần). Chúng ta phải đưa ra giả định rằng nếu trạng thái hiện tại đã là `READY`, thì Long-Running Process (tiến trình chạy dài hạn / quy trình nhiều bước) đã hoàn tất. Có thể bất kỳ lời gọi lệnh nào tiếp sau đó đều là do việc gửi lại thông báo, bởi nhóm phát triển đã chọn sử dụng cơ chế truyền thông điệp phân phối ít nhất một lần (at-least-once delivery). Dù trong trường hợp nào, chúng ta cũng không cần lo lắng vì thao tác mang tính lũy đẳng cho phép bỏ qua một cách an toàn mọi tác động từ hạ tầng và kiến trúc khi cần thiết. Hơn nữa, trong trường hợp cụ thể này, chúng ta không cần phải thiết kế thêm một `ProductChangeTracker` như đã làm với các lớp con của `Member` và `MemberChangeTracker` của chúng. Việc `discussion` đang ở trạng thái `READY` đã cung cấp toàn bộ thông tin cần thiết.

Tuy nhiên, cách tiếp cận tổng thể này vẫn có thể gặp vấn đề. Điều gì sẽ xảy ra nếu Long-Running Process gặp trục trặc bắt nguồn từ cơ chế truyền thông điệp? Làm thế nào để chúng ta đảm bảo tiến trình này được chạy trọn vẹn đến đích? Chà, có lẽ đã đến lúc "cậu thiếu niên" cần phải trưởng thành hơn một chút rồi đấy.

> 💡 **Giải thích thêm:** Tác giả sử dụng hình ảnh ẩn dụ "cậu thiếu niên cần trưởng thành hơn một chút" ("time for the teenager to grow up a little") để ám chỉ rằng thiết kế hiện tại của hệ thống xử lý tiến trình còn khá non nớt, chỉ hoạt động tốt trong kịch bản lý tưởng (happy path). Khi đối mặt với thế giới thực đầy biến động của hệ thống phân tán (mạng chập chờn, mất thông điệp, nghẽn tải), hệ thống cần một cơ chế trưởng thành, vững chãi hơn: cụ thể là bổ sung máy trạng thái (State Machine), bộ đếm thời gian hết hạn (Time-out Tracker) và cơ chế tự động thử lại (Retry) bền bỉ.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

## Process State Machines and Time-out Trackers

Chúng ta có thể làm cho tiến trình này trưởng thành hơn bằng cách bổ sung một khái niệm tương tự như đã mô tả trong phần Long-Running Processes (Chương 4). Các lập trình viên của SaaSOvation đã tạo ra một khái niệm có thể tái sử dụng và đặt tên cho nó là `TimeConstrainedProcessTracker`. Bộ theo dõi (tracker) này giám sát các tiến trình có khoảng thời gian phân bổ để hoàn thành đã hết hạn, cũng như các tiến trình có thể được thử lại bất kỳ số lần nào trước khi hết hạn. Thiết kế của tracker cho phép thử lại theo các khoảng thời gian cố định nếu muốn, và cuối cùng có thể hết thời gian chờ hoàn toàn (time-out) sau khi không thực hiện lần thử lại nào, hoặc sau một số lần thử lại nhất định.

Để làm rõ, tracker không phải là một phần của Core Domain (miền nghiệp vụ cốt lõi). Nó là một phần của một Technical Subdomain (phân miền kỹ thuật phụ trợ) mà bất kỳ dự án nào của SaaSOvation cũng có thể tái sử dụng. Điều này đồng nghĩa rằng trong một số trường hợp, chúng ta không cần quá bận tâm đến các quy tắc của Aggregate khi lưu trữ (persist) tracker và sửa đổi chúng sau đó. Các tracker tương đối biệt lập và thường không phải đối mặt với xung đột tương tranh (concurrency conflicts) do chúng có mối quan hệ một-một với tiến trình liên quan. Tuy nhiên, nếu xung đột xảy ra, chúng ta có thể dựa vào cơ chế thử lại của hệ thống truyền thông điệp để giải quyết. Mọi ngoại lệ xảy ra trong quá trình chuyển phát thông báo sẽ khiến listener gửi phản hồi NAK (Negative Acknowledgment - tín hiệu báo nhận thất bại / từ chối nhận thông điệp), từ đó kích hoạt RabbitMQ (hệ thống hàng đợi thông điệp) gửi lại thông điệp đó. Dẫu vậy, chúng ta không dự đoán rằng sẽ cần đến một số lượng lớn các lần thử lại.

Chính `Product` là đối tượng nắm giữ trạng thái hiện tại của tiến trình, và trong ngữ cảnh đó, một tracker sẽ xuất bản Sự kiện sau khi chạm đến khoảng thời gian thử lại, hoặc khi tiến trình được giám sát bị quá hạn hoàn toàn:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000545_436c231303bd619dbd78795591a0abb663d437c08b12ed65db4085189b5e5b41.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000546_86405122465c975e9f88fa6514cbbed2b2c045c089272f14b8efec4ee0f0c575.png)

```java
package com.saasovation.agilepm.domain.model.product;

import com.saasovation.common.domain.model.process.ProcessId;
import com.saasovation.common.domain.model.process.ProcessTimedOut;

public class ProductDiscussionRequestTimedOut extends ProcessTimedOut {
    public ProductDiscussionRequestTimedOut(
            String aTenantId,
            ProcessId aProcessId,
            int aTotalRetriesPermitted,
            int aRetryCount) {
        super(aTenantId, aProcessId, aTotalRetriesPermitted, aRetryCount);
    }
}

```

Các Event kế thừa từ lớp `ProcessTimedOut` được tracker sử dụng khi đạt đến khoảng thời gian thử lại hoặc khi đã hết thời gian hoàn toàn. Các Event listener có thể sử dụng phương thức `hasFullyTimedOut()` của Event để xác định xem sự kiện đó biểu thị việc hết thời gian hoàn toàn hay chỉ là một lần thử lại. Nếu việc thử lại được cho phép, giả định rằng các listener có quyền truy cập vào lớp `ProcessTimedOut`, chúng có thể truy vấn Event để lấy các chỉ báo và giá trị như `allowsRetries()`, `retryCount()`, `totalRetriesPermitted()` và `totalRetriesReached()`.

Được trang bị khả năng nhận thông báo về việc thử lại và hết thời gian, chúng ta có thể đưa `Product` tham gia vào một tiến trình tốt hơn. Trước tiên, chúng ta cần khởi động tiến trình, và điều này có thể thực hiện từ chính `ProductDiscussionRequestedListener` hiện có:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...
public class ProductDiscussionRequestedListener extends ExchangeListener {
    @Override
    protected void filteredDispatch(
            String aType,
            String aTextMessage) {
        NotificationReader reader = new NotificationReader(aTextMessage);
        if (!reader.eventBooleanValue("requestingDiscussion")) {
            return;
        }
        String tenantId = reader.eventStringValue("tenantId.id");
        String productId = reader.eventStringValue("product.id");

```

## INTEGRATION USING MESSAGING

```java
        productService.startDiscussionInitiation(
                new StartDiscussionInitiationCommand(
                        tenantId,
                        productId));
        // gửi lệnh tới Collaboration Context
        ...
    }
    ...
}

```

`ProductService` tạo ra tracker, lưu trữ nó, đồng thời liên kết tiến trình này với `Product` tương ứng:

```java
package com.saasovation.agilepm.application;
...
public class ProductService ... {
    ...
    @Transactional
    public void startDiscussionInitiation(
            StartDiscussionInitiationCommand aCommand) {
        Product product = productRepository
                .productOfId(
                        new TenantId(aCommand.getTenantId()),
                        new ProductId(aCommand.getProductId()));
        if (product == null) {
            throw new IllegalStateException(
                    "Unknown product of tenant id: "
                    + aCommand.getTenantId()
                    + " and product id: "
                    + aCommand.getProductId());
        }
        String timedOutEventName = ProductDiscussionRequestTimedOut.class.getName();
        TimeConstrainedProcessTracker tracker = new TimeConstrainedProcessTracker(
                product.tenantId().id(),
                ProcessId.newProcessId(),
                "Create discussion for product: " + product.name(),
                new Date(),
                5L * 60L * 1000L, // thử lại mỗi 5 phút một lần
                3, // tổng cộng 3 lần thử lại
                timedOutEventName);
        processTrackerRepository.add(tracker);

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000547_8f7ed333237bdb070b571b71e73fee7f95fea64800af3be8fb90ce04e6b1caae.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000548_e8238cb61588df39ad37e3d6e0e1278ca7dd1ab7d414e24b5bb11448a91d75c9.png)

```java
        product.setDiscussionInitiationId(
                tracker.processId().id());
    }
    ...
}

```

`TimeConstrainedProcessTracker` được khởi tạo để thử lại 3 lần, mỗi lần cách nhau 5 phút nếu cần thiết. Đúng là bình thường chúng ta không nên hard-code (viết cứng) các giá trị này, nhưng việc làm như vậy giúp chúng ta thấy rõ cách thức tracker được tạo ra.

## Did You Detect a Possible Problem Here?

Đặc tả thử lại mà chúng ta đang sử dụng có thể dẫn đến nhiều vấn đề nếu không cẩn thận, nhưng tạm thời chúng ta cứ giữ nguyên thiết kế như hiện tại và coi như mọi thứ đều ổn thoả.

Chính cách tiếp cận tạo ra tracker đại diện cho `Product` này là lời giải thích thỏa đáng nhất cho lý do tại sao chúng ta xử lý sự kiện `ProductCreated` cục bộ, thay vì để nó được diễn giải trực tiếp bên trong Collaboration Context. Điều này mang lại cho hệ thống của chúng ta cơ hội thiết lập cơ chế quản lý tiến trình và tách rời (decouple) sự kiện `ProductCreated` khỏi lệnh trong Collaboration Context, cụ thể là `CreateExclusiveDiscussion`.

Một bộ đếm thời gian chạy ngầm (background timer) sẽ kích hoạt định kỳ để kiểm tra thời gian đã trôi qua của các tiến trình. Bộ đếm thời gian này sẽ ủy quyền xử lý cho phương thức `checkForTimedOutProcesses()` trong `ProcessService`:

```java
package com.saasovation.agilepm.application;
...
public class ProcessService ... {
    ...
    @Transactional
    public void checkForTimedOutProcesses() {
        Collection<TimeConstrainedProcessTracker> trackers =
                processTrackerRepository.allTimedOut();
        for (TimeConstrainedProcessTracker tracker : trackers) {
            tracker.informProcessTimedOut();
        }
    }
    ...
}

```

Chính phương thức `informProcessTimedOut()` của tracker sẽ xác nhận xem có cần thử lại hay cho hết hạn một tiến trình hay không, và nếu được xác nhận, nó sẽ phát ra lớp con của Sự kiện `ProcessTimedOut`.

Tiếp theo, chúng ta cần thêm một listener mới để xử lý các lượt thử lại và hết thời gian chờ. Tối đa ba lần thử lại có thể diễn ra sau mỗi năm phút tùy theo nhu cầu. Đó là `ProductDiscussionRetryListener`:

```java
package com.saasovation.agilepm.infrastructure.messaging;
...
public class ProductDiscussionRetryListener extends ExchangeListener {
    @Autowired
    private ProcessService processService;
    ...
    @Override
    protected String exchangeName() {
        return Exchanges.AGILEPM_EXCHANGE_NAME;
    }

    @Override
    protected void filteredDispatch(
            String aType,
            String aTextMessage) {
        Notification notification = NotificationSerializer
                .instance()
                .deserialize(aTextMessage, Notification.class);
        ProductDiscussionRequestTimedOut event = notification.event();

        if (event.hasFullyTimedOut()) {
            productService.timeOutProductDiscussionRequest(
                    new TimeOutProductDiscussionRequestCommand(
                            event.tenantId(),
                            event.processId().id(),
                            event.occurredOn()));
        } else {
            productService.retryProductDiscussionRequest(
                    new RetryProductDiscussionRequestCommand(
                            event.tenantId(),
                            event.processId().id()));
        }
    }

    @Override
    protected String[] listensToEvents() {
        return new String[] {
            "com.saasovation.agilepm.process.ProductDiscussionRequestTimedOut"
        };
    }
}

```

Listener này chỉ quan tâm đến các Sự kiện `ProductDiscussionRequestTimedOut` và được thiết kế để hoạt động với mọi hoán vị số lần thử lại và hết hạn thời gian. Chính tiến trình và tracker sẽ xác định số lần nó có thể nhận thông báo. Các Sự kiện sẽ được gửi theo một trong hai điều kiện: Tiến trình có thể đã hết thời gian hoàn toàn, hoặc đó có thể là một thông báo yêu cầu thử lại thao tác. Trong cả hai trường hợp, listener đều điều phối (dispatch) lời gọi tới `ProductService`. Nếu xảy ra tình trạng hết thời gian hoàn toàn, Application Service sẽ xử lý tình huống này:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000549_cc2c1065cfc6be3dfd753d23a8cf8d931e7ea2f104f68949ff02c4bd4cfe9ab5.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000550_9ec25067def09a43e27ba540ae4ab5285ea0f4bac79e22ae8135ef0f5d8bbefb.png)

```java
package com.saasovation.agilepm.application;
...
public class ProductService ... {
    ...
    @Transactional
    public void timeOutProductDiscussionRequest(
            TimeOutProductDiscussionRequestCommand aCommand) {
        ProcessId processId = ProcessId.existingProcessId(
                aCommand.getProcessId());
        TenantId tenantId = new TenantId(aCommand.getTenantId());
        Product product = productRepository
                .productOfDiscussionInitiationId(
                        tenantId,
                        processId.id());
        this.sendEmailForTimedOutProcess(product);
        product.failDiscussionInitiation();
    }
    ...
}

```

Đầu tiên, một email được gửi tới product owner (chủ sở hữu sản phẩm) để thông báo rằng việc thiết lập cuộc thảo luận đã thất bại, sau đó `Product` được đánh dấu là khởi tạo thảo luận thất bại. Như có thể thấy từ phương thức mới `failDiscussionInitiation()` của `Product`, chúng ta cần khai báo thêm một trạng thái `FAILED` trong `DiscussionAvailability`. Phương thức `failDiscussionInitiation()` thực hiện cơ chế bù trừ (compensation) đơn giản cần thiết để giữ cho `Product` luôn ở trạng thái hợp lệ và toàn vẹn:

```java
package com.saasovation.agilepm.domain.model.product;
...
public class Product extends ConcurrencySafeEntity {
    ...
    public void failDiscussionInitiation() {
        if (!this.discussion().availability().isReady()) {
            this.setDiscussionInitiationId(null);

```

## INTEGRATION USING MESSAGING

```java
            this.setDiscussion(
                    ProductDiscussion
                            .fromAvailability(
                                    DiscussionAvailability.FAILED));
        }
    }
    ...
}

```

Điều có thể còn thiếu ở đây là một Sự kiện `DiscussionRequestFailed` mới cần được phát ra bởi `failDiscussionInitiation()`. Nhóm phát triển sẽ phải cân nhắc những lợi ích tiềm năng của việc này. Trên thực tế, việc gửi email cho product owner và các tài nguyên quản trị khác có lẽ sẽ được xử lý tốt nhất như là hệ quả của chính Sự kiện đó. Rốt cuộc thì điều gì sẽ xảy ra nếu phương thức `timeOutProductDiscussionRequest()` của `ProductService` gặp sự cố khi gửi email? Mọi chuyện có thể trở nên rất rắc rối và phiền toái. (Aha!) Nhóm phát triển đã ghi nhận điều này và sẽ quay lại giải quyết sau.

Mặt khác, nếu Sự kiện chỉ ra rằng cần phải thử lại, listener sẽ ủy quyền cho thao tác sau trong `ProductService`:

```java
package com.saasovation.agilepm.application;
...
public class ProductService ... {
    ...
    @Transactional
    public void retryProductDiscussionRequest(
            RetryProductDiscussionRequestCommand aCommand) {
        ProcessId processId = ProcessId.existingProcessId(
                aCommand.getProcessId());
        TenantId tenantId = new TenantId(aCommand.getTenantId());
        Product product = productRepository
                .productOfDiscussionInitiationId(
                        tenantId,
                        processId.id());
        if (product == null) {
            throw new IllegalStateException(
                    "Unknown product of tenant id: "
                    + aCommand.getTenantId()
                    + " and discussion initiation id: "
                    + processId.id());
        }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000551_e8fb0ea87c0751a5392997fa981470443db63263ed8dd77615f7a17c53f6ecb1.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000552_815c8b6d554b1fba849d1fd6a0e57c8b05d63d8f21429320ac63551066695213.png)

## Chapter 13 INTEGRATING BOUNDED CONTEXTS

```java
        this.requestProductDiscussion(
                new RequestProductDiscussionCommand(
                        aCommand.getTenantId(),
                        product.productId().id()));
    }
    ...
}

```

`Product` được lấy ra từ Repository (kho lưu trữ đối tượng nghiệp vụ) của nó thông qua `ProcessId` liên kết vốn được thiết lập trên thuộc tính `discussionInitiationId` của `Product`. Sau khi lấy được `Product`, `ProductService` sẽ sử dụng nó (tự ủy quyền - self-delegation) để yêu cầu tạo lại cuộc thảo luận.

Cuối cùng, chúng ta đạt được kết quả mong muốn. Khi cuộc thảo luận được khởi tạo thành công, Collaboration Context sẽ phát ra sự kiện `DiscussionStarted`. Ngay sau đó, `DiscussionStartedListener` của chúng ta trong Agile Project Management Context sẽ nhận được thông báo và điều phối tới `ProductService` như trước. Tuy nhiên, lần này có thêm một hành vi mới:

```java
package com.saasovation.agilepm.application;
...
public class ProductService ... {
    ...
    @Transactional
    public void initiateDiscussion(
            InitiateDiscussionCommand aCommand) {
        Product product = productRepository
                .productOfId(
                        new TenantId(aCommand.getTenantId()),
                        new ProductId(aCommand.getProductId()));
        if (product == null) {
            throw new IllegalStateException(
                    "Unknown product of tenant id: "
                    + aCommand.getTenantId()
                    + " and product id: "
                    + aCommand.getProductId());
        }
        product.initiateDiscussion(
                new DiscussionDescriptor(
                        aCommand.getDiscussionId()));
        TimeConstrainedProcessTracker tracker =
                this.processTrackerRepository.trackerOfProcessId(
                        ProcessId.existingProcessId(
                                product.discussionInitiationId()));

```

```java
        tracker.completed();
    }
    ...
}

```

`ProductService` hiện đã cung cấp hành vi kết thúc cho tiến trình, thông báo cho tracker biết rằng nó đã `completed()`. Kể từ thời điểm này trở đi, tracker sẽ không còn được chọn làm bộ thông báo thử lại hoặc hết thời gian nữa. Tiến trình đã hoàn tất.

Mặc dù chúng ta có thể đang cảm thấy hài lòng với kết quả này, nhưng thiết kế này vẫn tồn tại một chút vấn đề. Với tình hình hiện tại, việc thử lại các yêu cầu tạo cuộc thảo luận cho `Product` có thể dẫn đến một số rắc rối nếu chúng ta giữ nguyên thiết kế của Collaboration Context như hiện tại. Vấn đề cơ bản là các thao tác trong Collaboration Context hiện chưa có tính lũy đẳng (not idempotent). Dưới đây là phân tích chi tiết về khiếm khuyết thiết kế nhỏ này và những việc cần làm để khắc phục:

* Do cơ chế chuyển phát thông điệp được đảm bảo ít nhất một lần (at-least-once delivery) đang được áp dụng, nên ngay khi một thông điệp được gửi tới exchange, chắc chắn nó sẽ đến được (các) listener trong một khoảng thời gian nhất định. Nếu có sự chậm trễ trong việc tạo các đối tượng cộng tác mới và điều này dẫn đến dù chỉ một lần thử lại, thì lần thử lại đó sẽ kéo theo việc gửi nhiều lần cùng một lệnh `CreateExclusiveDiscussion`. Tất cả các lệnh như vậy cuối cùng đều sẽ được chuyển phát. Do đó, bất kỳ lần thử lại nào cũng sẽ khiến Collaboration Context cố gắng tạo cùng một `Forum` và `Discussion` nhiều lần. Trên thực tế, chúng ta sẽ không gặp phải tình trạng trùng lặp dữ liệu vì các ràng buộc tính duy nhất (uniqueness constraints) đã được áp đặt trên các thuộc tính của `Forum` và `Discussion`. Vì vậy, các lỗi phát sinh do cố gắng tạo nhiều lần rốt cuộc sẽ là lành tính (benign). Tuy nhiên, dưới góc độ của nhật ký lỗi (error logs), những lần thử thất bại này sẽ trông như thể xuất phát từ lỗi phần mềm (bugs). Câu hỏi đặt ra là: Trong khi chúng ta vẫn muốn quy định thời gian chờ kết thúc toàn bộ tiến trình (complete process time-out), liệu có nên vô hiệu hóa các lần thử lại định kỳ hay không?
* Mặc dù có vẻ như giải pháp là vô hiệu hóa việc thử lại trong Agile Project Management Context, nhưng mấu chốt vấn đề là chúng ta cần phải làm cho các thao tác của Collaboration Context trở nên có tính lũy đẳng (idempotent). Hãy nhớ rằng RabbitMQ đảm bảo chuyển phát ít nhất một lần và do đó có thể chuyển phát cùng một thông điệp lệnh nhiều lần, ngay cả khi nó chỉ được gửi một lần duy nhất. Việc làm cho các thao tác cộng tác có tính lũy đẳng sẽ ngăn chặn mọi nỗ lực tạo cùng một `Forum` và `Discussion` nhiều lần, đồng thời dập tắt việc ghi nhật ký các lỗi lành tính không đáng có.
* Agile Project Management Context hoàn toàn có thể gặp lỗi khi cố gắng gửi lệnh `CreateExclusiveDiscussion`. Nếu việc gửi thông điệp gặp sự cố, cần phải hết sức cẩn trọng để đảm bảo

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000553_df649eb286bab05854dbbf978ffcf5e8f3f6a3433ff194c6b3079148074db942.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000554_c5146acf5004433dfe6c40058f3e79d91219e12e96499d5ee218c3e2476e0d0c.png)

rằng việc gửi lại sẽ được thử cho đến khi thành công. Nếu không, yêu cầu tạo `Forum` và `Discussion` sẽ không bao giờ được thực hiện. Chúng ta có thể đảm bảo các nỗ lực gửi lại lệnh theo một vài cách. Nếu việc gửi thông điệp thất bại, chúng ta có thể ném ra một ngoại lệ từ `filteredDispatch()`, điều này sẽ khiến thông điệp bị phản hồi NAK. Kết quả là RabbitMQ sẽ nhận thấy cần phải chuyển phát lại thông báo Sự kiện `ProductCreated` hoặc `ProductDiscussionRequested`, và `ProductDiscussionRequestedListener` của chúng ta sẽ nhận lại thông báo đó. Cách khác để xử lý việc này là chỉ đơn giản thử gửi lại cho đến khi thành công, có thể kết hợp sử dụng thuật toán Capped Exponential Back-off (thuật toán lùi theo cấp số nhân có giới hạn trần). Trong trường hợp RabbitMQ bị ngoại tuyến (offline), các lần thử lại có thể thất bại trong một khoảng thời gian khá dài. Do đó, việc kết hợp giữa NAK thông điệp và thử lại có thể là cách tiếp cận tốt nhất. Dẫu vậy, nếu tiến trình của chúng ta thử lại ba lần, mỗi lần cách nhau năm phút, thì đó có thể đã là tất cả những gì chúng ta cần. Rốt cuộc, một khi tiến trình bị hết hạn thời gian hoàn toàn, nó sẽ gửi một email yêu cầu sự can thiệp của con người.

Cuối cùng, nếu `ExclusiveDiscussionCreationListener` của Collaboration Context có thể ủy quyền cho một thao tác mang tính lũy đẳng trong Application Service, nó sẽ giải quyết được rất nhiều vấn đề của chúng ta:

```java
package com.saasovation.collaboration.application;
...
public class ForumService ... {
    ...
    @Transactional
    public Discussion startExclusiveForumWithDiscussion(
            String aTenantId,
            String aCreatorId,
            String aModeratorId,
            String aForumSubject,
            String aForumDescription,
            String aDiscussionSubject,
            String anExclusiveOwner) {
        Tenant tenant = new Tenant(aTenantId);
        Forum forum = forumRepository
                .exclusiveForumOfOwner(
                        tenant,
                        anExclusiveOwner);
        if (forum == null) {
            forum = this.startForum(
                    tenant,
                    aCreatorId,
                    aModeratorId,
                    aForumSubject,

```

```java
                    aForumDescription,
                    anExclusiveOwner);
        }
        Discussion discussion = discussionRepository
                .exclusiveDiscussionOfOwner(
                        tenant,
                        anExclusiveOwner);
        if (discussion == null) {
            Author author = collaboratorService
                    .authorFrom(
                            tenant,
                            aModeratorId);
            discussion = forum.startDiscussion(
                    forumNavigationService,
                    author,
                    aDiscussionSubject);
            discussionRepository.add(discussion);
        }
        return discussion;
    }
    ...
}

```

Bằng cách cố gắng tìm kiếm `Forum` và `Discussion` dựa trên thuộc tính chủ sở hữu độc quyền (exclusive owner) duy nhất của chúng, chúng ta ngăn chặn được việc cố tạo ra hai thực thể Aggregate vốn có thể đã tồn tại. Thật tuyệt vời, chỉ một vài dòng code đã giúp quá trình xử lý hướng sự kiện (Event-Driven) của chúng ta trở nên tốt hơn rất nhiều!

## Designing a More Sophisticated Process

Dù vậy, chúng ta vẫn có thể mong muốn thiết kế một tiến trình tinh vi hơn. Trong những trường hợp cần có nhiều bước hoàn thành, giải pháp tốt nhất là sở hữu một State Machine (máy trạng thái) phức tạp và chi tiết hơn. Để đáp ứng các nhu cầu như vậy, dưới đây là định nghĩa của một interface `Process`:

```java
package com.saasovation.common.domain.model.process;

import java.util.Date;

public interface Process {

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000555_3e8a8495f351b88a105cad4ae2a83c7d2534f22770ea2db2c770709ccc199c41.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000556_240c7d050dc6ab8f438a94a406e717b0601581305a8be6df556149d332e00d34.png)

```java
    public enum ProcessCompletionType {
        NotCompleted,
        CompletedNormally,
        TimedOut
    }

    public long allowableDuration();
    public boolean canTimeout();
    public long currentDuration();
    public String description();
    public boolean didProcessingComplete();
    public void informTimeout(Date aTimedOutDate);
    public boolean isCompleted();
    public boolean isTimedOut();
    public boolean notCompleted();
    public ProcessCompletionType processCompletionType();
    public ProcessId processId();
    public Date startTime();
    public TimeConstrainedProcessTracker timeConstrainedProcessTracker();
    public Date timedOutDate();
    public long totalAllowableDuration();
    public int totalRetriesPermitted();
}

```

Dưới đây là một số thao tác quan trọng nhất được cung cấp bởi `Process`:

* `allowableDuration()` : Nếu `Process` có thể bị hết hạn thời gian, phương thức này trả về tổng khoảng thời gian hoặc khoảng thời gian giữa các lần thử lại.
* `canTimeout()` : Nếu `Process` có thể bị hết hạn thời gian, phương thức này trả về `true`.
* `timeConstrainedProcessTracker()` : Nếu `Process` có thể bị hết hạn thời gian, phương thức này trả về một đối tượng `TimeConstrainedProcessTracker` mới và duy nhất.
* `totalAllowableDuration()` : Trả về tổng thời lượng cho phép của `Process`. Nếu không cho phép thử lại, kết quả trả về là `allowableDuration()`. Nếu cho phép thử lại, kết quả là `allowableDuration()` nhân với `totalRetriesPermitted()`.
* `totalRetriesPermitted()` : Nếu `Process` cho phép hết thời gian và thử lại, phương thức này trả về tổng số lần thử lại có thể thực hiện.

Các lớp triển khai `Process` có thể được giám sát về việc hết thời gian chờ và thử lại dưới sự kiểm soát của `TimeConstrainedProcessTracker` mà chúng ta đã quen thuộc. Khi đã tạo ra `Process`, chúng ta có thể yêu cầu nó cung cấp một tracker duy nhất. Bài kiểm thử này chỉ ra cách hai đối tượng phối hợp hoạt động với nhau, phần lớn tương tự như cách `Product` đã hoạt động với tracker của nó:

```java
Process process = new TestableTimeConstrainedProcess(
        TENANT_ID,
        ProcessId.newProcessId(),
        "Testable Time Constrained Process",
        5000L);
TimeConstrainedProcessTracker tracker = process.timeConstrainedProcessTracker();

process.confirm1();
assertFalse(process.isCompleted());
assertFalse(process.didProcessingComplete());
assertEquals(process.processCompletionType(), ProcessCompletionType.NotCompleted);

process.confirm2();
assertTrue(process.isCompleted());
assertTrue(process.didProcessingComplete());
assertEquals(process.processCompletionType(), ProcessCompletionType.CompletedNormally);
assertNull(process.timedOutDate());

tracker.informProcessTimedOut();
assertFalse(process.isTimedOut());

```

`Process` được tạo ra bởi bài kiểm thử này phải hoàn thành (không có lần thử lại nào) trong vòng năm giây (`5000L` mili giây), và nó sẽ luôn luôn làm được điều đó. `Process` sẽ chỉ được đánh dấu là đã hoàn thành và xử lý trọn vẹn sau khi cả hai phương thức `confirm1()` và `confirm2()` đều đã được kích hoạt. Ở bên trong, `Process` biết rằng cả hai trạng thái đều phải được xác nhận:

```java
public class TestableTimeConstrainedProcess extends AbstractProcess {
    ...
    public void confirm1() {
        this.confirm1 = true;
        this.completeProcess(ProcessCompletionType.CompletedNormally);
    }

    public void confirm2() {
        this.confirm2 = true;

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000557_87c268d244d9ee933faf5edb28812e6a372126aa080c85aa4d5d458484205010.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000558_9e55f4f152c0506cfc6cee656873f826eccd4c52891e3fbc458a449f1af0f8ac.png)

```java
        this.completeProcess(ProcessCompletionType.CompletedNormally);
    }
    ...
    protected boolean completenessVerified() {
        return this.confirm1 && this.confirm2;
    }

    protected void completeProcess(
            ProcessCompletionType aProcessCompletionType) {
        if (!this.isCompleted() && this.completenessVerified()) {
            this.setProcessCompletionType(aProcessCompletionType);
        }
    }
    ...
}

```

Ngay cả khi `Process` này tự gọi phương thức `completeProcess()`, nó vẫn không thể được đánh dấu là đã hoàn tất cho đến khi `completenessVerified()` trả về giá trị `true`. Phương thức đó sẽ chỉ trả về `true` khi cả hai cờ `confirm1` và `confirm2` đều được đặt thành `true`. Nói cách khác, cả hai thao tác `confirm1()` và `confirm2()` đều phải được thực thi. Do đó, phương thức `completenessVerified()` cho phép xác nhận nhiều bước xử lý đã hoàn thành trước khi toàn bộ `Process` được coi là hoàn tất, và mỗi loại `Process` chuyên biệt đều có thể có định nghĩa `completenessVerified()` của riêng mình.

Vậy điều gì sẽ xảy ra khi bước cuối cùng của bài kiểm thử này được chạy?

```java
...
tracker.informProcessTimedOut();
assertFalse(process.isTimedOut());

```

Dựa vào trạng thái nội bộ của mình, tracker biết rằng `Process` trên thực tế chưa hề bị quá hạn thời gian. Do đó, khẳng định (assertion) trong dòng code tiếp theo sẽ luôn đánh giá là `false` đối với việc bị timeout. (Tất nhiên, chúng ta giả định rằng toàn bộ bài kiểm thử sẽ hoàn thành trong vòng dưới năm giây, và hoàn toàn tin tưởng điều này sẽ luôn đúng trong các điều kiện kiểm thử thông thường.)

Lớp cơ sở `AbstractProcess` triển khai interface `Process`, đóng vai trò như một Adapter (mẫu thiết kế chuyển đổi giao diện / bộ tương thích), và cung cấp một phương thức rất dễ dàng để phát triển một Long-Running Process tinh vi hơn. Vì `AbstractProcess` kế thừa từ lớp cơ sở `Entity` (thực thể), nên rất dễ dàng để thiết kế một Aggregate đóng vai trò như một `Process`. Chẳng hạn, chúng ta có thể cho `Product` kế thừa từ `AbstractProcess`, mặc dù nó không đòi hỏi mức độ phức tạp đến vậy. Dẫu thế, chúng ta có thể hình dung việc tận dụng cách tiếp cận này để đáp ứng một tiến trình phức tạp hơn, đồng thời yêu cầu phương thức `completenessVerified()` xác định xem tất cả các bước bắt buộc đã hoàn thành hay chưa.

## When Messaging or Your System Is Unavailable

Không có một cách tiếp cận đơn lẻ nào trong việc phát triển các hệ thống phần mềm phức tạp lại là một liều thuốc vạn năng. Bất kỳ phương pháp nào cũng luôn đi kèm với những vấn đề và hạn chế, một số trong đó chúng ta đã thảo luận. Một vấn đề đối với hệ thống truyền thông điệp là nó có thể trở nên không khả dụng (unavailable) trong một khoảng thời gian. Đây có thể là tình huống hiếm khi xảy ra, nhưng khi nó thực sự xảy ra, có một vài điều cần lưu ý.

Khi một cơ chế truyền thông điệp bị ngắt kết nối (offline) trong một khoảng thời gian, các bên xuất bản thông báo sẽ không thể gửi thông điệp qua nó. Vì tình huống này có thể được phát hiện bởi phía client xuất bản, giải pháp tốt nhất thường là lùi lại (back off - giãn tần suất) các nỗ lực gửi thông báo cho đến khi hệ thống truyền thông điệp hoạt động trở lại. Điều này sẽ trở nên rõ ràng ngay khi có bất kỳ một lượt gửi nào thành công. Nhưng cho đến thời điểm đó, hãy đảm bảo rằng các nỗ lực gửi thông điệp diễn ra với tần suất thưa hơn so với khi mọi thứ hoạt động bình thường. Việc giãn cách thời gian giữa các lần thử lại lên đến 30 giây hoặc 1 phút là hoàn toàn hợp lý. Hãy nhớ rằng, nếu hệ thống của bạn có một Event Store (kho lưu trữ sự kiện), các Event của bạn sẽ tiếp tục được xếp hàng đợi trong hệ thống đang hoạt động và có thể được gửi đi ngay khi hệ thống truyền thông điệp khả dụng trở lại.

Chắc chắn rằng các listener sẽ không nhận được các thông báo mang Event mới nếu hạ tầng truyền thông điệp biến mất trong một khoảng thời gian. Khi cơ chế truyền thông điệp hoạt động trở lại, liệu các client listener của bạn có được tự động kích hoạt lại hay không, hay bạn sẽ phải đăng ký (subscribe) lại cơ chế client phía consumer (bên tiêu thụ)? Nếu việc tự động khôi phục consumer không được hỗ trợ, bạn sẽ cần chắc chắn rằng các consumer của mình đã được đăng ký lại. Nếu không, cuối cùng bạn sẽ phát hiện ra một sự thật không mong muốn rằng Bounded Context của bạn không nhận được các thông báo cần thiết để duy trì tương tác với các Bounded Context mà nó phụ thuộc. Đó là một loại "eventual consistency" mà bạn chắc chắn muốn tránh xa.

Không phải lúc nào cơ chế truyền thông điệp cũng là nguồn cơn của các vấn đề liên quan đến thông điệp. Hãy xem xét tình huống này: Bounded Context của bạn không thể truy cập được trong một khoảng thời gian dài. Khi nó khả dụng trở lại, các durable exchanges/queues (hàng đợi / bộ trao đổi thông điệp bền vững) mà nó đăng ký đã tích lũy rất nhiều thông điệp chưa được chuyển phát. Một khi Bounded Context của bạn khởi động lại và đăng ký các consumer của nó, hệ thống có thể cần một lượng thời gian đáng kể để tiếp nhận và xử lý toàn bộ các thông báo đang tồn đọng đó. Có thể bạn không làm được gì nhiều trước tình huống này ngoài việc kiên trì theo đuổi các mục tiêu giới hạn thời gian chết (limited downtime), xây dựng cơ chế triển khai không gián đoạn ("live" deployment), và thiết kế hệ thống với các node dự phòng (cluster - cụm máy chủ) để việc mất một node không làm toàn bộ hệ thống ngừng hoạt động. Tuy nhiên, vẫn có những thời điểm bạn không thể tránh khỏi một khoảng thời gian chết (downtime). Ví dụ: nếu việc thay đổi mã nguồn ứng dụng đòi hỏi phải thay đổi cơ sở dữ liệu và bạn không thể vá lỗi (patch) các thay đổi này mà không gây ra sự cố, bạn sẽ cần hệ thống có một khoảng thời gian chết. Trong những trường hợp như vậy, tiến trình tiêu thụ thông điệp của bạn đơn giản là sẽ phải "chạy đuổi theo" để bắt kịp lượng tồn đọng. Rõ ràng đây là tình huống chúng ta cần nhận thức được và lên kế hoạch phòng tránh hoặc giải quyết nếu nó trở thành một vấn đề.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000559_2c0aa5e14e4dc2deaf241c37bd3ef9d22dd0867e8f4ca56bc005e1ad38c2bf68.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000560_29d0ece12241199822e87c83c9613960f0ea2b37accde6bd0c31acf99640eba3.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000561_24854c064f7c827fa52b38b85f939f78952a91dfd5320d4cd4eadcaf7bf965fe.png)

## Wrap-Up

Trong chương này, chúng ta đã xem xét các cách khác nhau để tích hợp thành công nhiều Bounded Context.

* Chúng ta đã xem lại tư duy cơ bản cần thiết để tích hợp thành công trong môi trường điện toán phân tán.
* Chúng ta đã xem xét cách tích hợp nhiều Context thông qua tài nguyên RESTful (kiến trúc dịch vụ web dựa trên REST).
* Bạn đã được xem một số ví dụ về việc tích hợp bằng truyền thông điệp, bao gồm cách phát triển và quản lý các Long-Running Process, từ đơn giản đến phức tạp.
* Bạn đã hiểu rõ những thách thức phải đối mặt khi quyết định nhân bản thông tin giữa các Bounded Context, cũng như cách quản lý và phòng tránh tình trạng này.
* Bạn đã thu được nhiều lợi ích khi xem xét từ các ví dụ đơn giản, sau đó tiến tới các ví dụ phức tạp hơn đòi hỏi độ chín muồi ngày càng cao trong thiết kế.

Giờ đây, sau khi đã tìm hiểu cách tích hợp nhiều Bounded Context, chúng ta hãy cùng quay trở lại tập trung vào một Bounded Context đơn lẻ và xem cách thiết kế các thành phần của ứng dụng bao quanh domain model.

## Chapter 14

## Application

Any program is only as good as it is useful. -Linus Torvalds

Một domain model thường nằm ở trung tâm của một ứng dụng. Ứng dụng đó có thể có một giao diện người dùng hiển thị các khái niệm của domain model và cho phép người dùng thực hiện nhiều hành động khác nhau trên mô hình. Giao diện người dùng sẽ sử dụng các dịch vụ cấp ứng dụng (Application Services) để điều phối các tác vụ use case, quản lý giao dịch (transactions), và xác nhận các quyền hạn bảo mật cần thiết. Hơn nữa, giao diện người dùng, Application Services và domain model sẽ phụ thuộc vào sự hỗ trợ hạ tầng đặc thù của nền tảng doanh nghiệp. Các chi tiết triển khai hạ tầng nói chung sẽ bao gồm các tiện ích của một container thành phần, quản trị ứng dụng, truyền thông điệp, và cơ sở dữ liệu.

## Road Map to This Chapter

* Tìm hiểu một vài cách cung cấp dữ liệu của domain model để giao diện người dùng kết xuất (render).
* Xem cách các Application Service được triển khai, cùng các loại thao tác mà chúng thực hiện.
* Nghiên cứu các cách tách rời (decouple) đầu ra từ Application Services với các loại client khác nhau.
* Xem xét lý do tại sao bạn có thể cần kết hợp nhiều mô hình trong giao diện người dùng, và cách thực hiện điều đó.
* Học cách sử dụng hạ tầng để cung cấp các triển khai kỹ thuật cho ứng dụng.

Đôi khi chúng ta làm việc trên các mô hình tồn tại nhằm mục đích hỗ trợ các ứng dụng. Điều này đúng với Identity and Access Context. SaaSOvation nhận thấy cần phải tách riêng các mối quan tâm về quản lý định danh và truy cập, từ đó hình thành nên một mô hình hỗ trợ mà bản thân nó cũng sẽ đóng vai trò như một sản phẩm độc lập hoạt động theo mô hình thuê bao (subscription-based). Ngay cả trong trường hợp của IdOvation, chắc chắn nó cũng sẽ có giao diện người dùng quản trị và tự phục vụ (self-service) riêng. Đúng là các Generic Subdomain (phân miền dùng chung) và Supporting Subdomain (phân miền hỗ trợ) (Chương 2) đôi khi sẽ thiếu vắng tất cả các thành phần bổ trợ đi kèm với một ứng dụng hoàn chỉnh, và điều đó hoàn toàn bình thường. Khi một mô hình tồn tại chỉ để hỗ trợ một mô hình khác, mô hình hỗ trợ đó có thể đơn giản chỉ là một tập hợp các lớp trong một Module (Chương 9) riêng biệt nhằm giải quyết một khái niệm chuyên biệt và cung cấp một số thuật toán. 1 Những mô hình khác sẽ đòi hỏi ít nhất một số trải nghiệm người dùng tương tác thực tế và các thành phần ứng dụng. Chương này tập trung vào dạng mô hình thứ hai - tức là dạng mô hình phức tạp hơn.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000562_a7e1154b53f39692d81c1d83d17c59c2e9caa74a101f98a3a0c2219f32dbc80b.png)

Ở đây, chúng tôi sử dụng thuật ngữ application gần như có thể hoán đổi cho nhau với system (hệ thống) và business service (dịch vụ nghiệp vụ). Tôi sẽ không cố gắng phân tích một cách hình thức xem tại thời điểm nào một ứng dụng trở thành một hệ thống, nhưng tôi cho rằng khi một ứng dụng phụ thuộc vào các ứng dụng hoặc dịch vụ khác thông qua việc tích hợp, thì toàn bộ giải pháp đó có thể được gọi là một hệ thống. Đôi khi các thuật ngữ application và system được sử dụng thay thế cho nhau để chỉ cùng một đối tượng, trong đó system thực chất mô tả những gì chúng ta thường gọi là một ứng dụng. Và một dịch vụ nghiệp vụ đơn lẻ cung cấp một vài hoặc nhiều điểm cuối dịch vụ kỹ thuật (endpoints) cũng có thể được gọi là một hệ thống theo nghĩa rộng. Mặc dù tôi không muốn làm rối rắm ranh giới phân biệt giữa ba khái niệm này, nhưng tôi muốn dùng một thuật ngữ thống nhất để có thể thảo luận về những mối quan tâm và trách nhiệm chung của cả ba.

## What's an Application?

Tóm lại, tôi sử dụng thuật ngữ application để chỉ tập hợp tinh gọn nhất các thành phần được ghép nối với nhau nhằm tương tác và hỗ trợ một mô hình Core Domain (Chương 2). Điều này thường bao gồm bản thân domain model, một giao diện người dùng, các Application Service được sử dụng nội bộ, và các thành phần hạ tầng. Những thành phần chính xác nằm trong từng ngăn đó sẽ khác nhau giữa các ứng dụng và sẽ phụ thuộc vào các Kiến trúc (Chương 4) cụ thể đang được áp dụng.

Khi một ứng dụng mở các dịch vụ của mình ra ngoài thông qua lập trình, giao diện người dùng khi đó sẽ mang nghĩa rộng hơn và bao gồm một dạng API (Application Programming Interface - giao diện lập trình ứng dụng). Có nhiều cách khác nhau để mở các dịch vụ của nó, nhưng giao diện dạng này không dành cho con người sử dụng trực tiếp. Loại giao diện người dùng này đã được thảo luận trong chương Tích hợp các Bounded Context (Chương 13). Trong chương này, tôi đề cập đến các khía cạnh của giao diện người dùng dành cho con người, thường thuộc dạng giao diện đồ họa.

Đối với chủ đề này, tôi cố gắng tránh thiên vị bất kỳ Kiến trúc cụ thể nào. Tôi thể hiện sự tách biệt đó qua sơ đồ trông có vẻ khác lạ ở Hình 14.1, một sơ đồ cố ý không tuân theo bất kỳ kiến trúc điển hình nào. Các đường nét đứt với mũi tên rỗng thể hiện mối quan hệ hiện thực hóa (implementation) theo chuẩn UML, phản ánh Dependency Inversion Principle (DIP - nguyên lý đảo ngược phụ thuộc, Chương 4). Các đường nét liền với mũi tên hở biểu thị việc điều phối thao tác (operation dispatching). Ví dụ, tầng hạ tầng triển khai các interface trừu tượng từ giao diện người dùng, Application Services và domain model. Nó cũng điều phối các thao tác tới Application Services, domain model và kho dữ liệu (data store).

1. Để xem ví dụ về một Generic Subdomain là một mô hình độc lập, hãy xem 'Time and Money Code Library' của Eric Evans: http://timeandmoney.sourceforge.net/.

Figure 14.1 The primary application areas of concern, but without ties to any one architecture. These areas still emphasize the DIP with infrastructure dependent on abstractions of every other area.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000563_91cef0c3bad33346458e717649afed02c6afb3f8f008fd1b5262f779ab92e018.png)

Mặc dù không thể tránh khỏi việc sẽ có sự trùng lặp nhất định với một số phong cách kiến trúc, nhưng trọng tâm quan tâm của chúng ta trong chương này là những gì mà hầu như bất kỳ kiến trúc nào cũng cần phải thực hiện để duy trì các mục tiêu của ứng dụng. Ở những chỗ mà một kiến trúc cụ thể xuất hiện, tôi sẽ có phần ghi nhận rõ ràng.

Thật khó để không sử dụng thuật ngữ layer (tầng/lớp), như trong Layers Architecture (Kiến trúc phân lớp, Chương 4). Đó là một thuật ngữ hữu ích bất kể phong cách kiến trúc nào đang được thảo luận. Ví dụ, hãy xem xét nơi cư trú của các Application Service. Cho dù bạn coi Application Services nằm trong một chiếc vòng bao quanh domain model, trong một hình lục giác bao bọc mô hình, trong một khoang nối với bus thông điệp, hay trong một tầng nằm dưới giao diện người dùng và nằm trên mô hình, thì việc sử dụng thuật ngữ Application Layer để mô tả vị trí mang tính khái niệm đó hoàn toàn có thể chấp nhận được. Mặc dù tôi cố gắng hạn chế lạm dụng thuật ngữ này trong chương, nhưng layer rất hữu ích trong việc gán nhãn nơi các thành phần cư trú. Điều này chắc chắn không hàm ý rằng DDD chỉ giới hạn tồn tại duy nhất trong một Layers Architecture. 2

Tôi sẽ bắt đầu với giao diện người dùng, sau đó chuyển sang Application Services, rồi đến hạ tầng. Xuyên suốt từng chủ đề, tôi sẽ đề cập đến vị trí ăn khớp của mô hình, nhưng sẽ không đi sâu vào chi tiết nội tại của bản thân mô hình vì điều đó sẽ bị trùng lặp với các phần còn lại của cuốn sách.

2. Xem Chương 4 để biết thêm chi tiết.

511

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000564_89adefa4ace322dc945cac8c9cc88eec2ce1a3f7f080811abb6e06cae02a60ca.png)

## User Interface

Trên nền tảng Java, nền tảng .NET và các nền tảng khác, có quá nhiều framework giao diện người dùng đến mức việc đi sâu nghiên cứu ưu điểm của từng framework ở đây dường như không thú vị mà cũng chẳng mang lại nhiều giá trị thực tiễn.

Điều tốt nhất là nắm bắt được các phân loại khái quát hơn, vốn chủ yếu rơi vào các nhóm được mô tả trong danh sách sau. Chúng được liệt kê theo thứ tự mức độ "nặng nề" (heaviness), chứ không phải theo mức độ phổ biến. Tại thời điểm viết cuốn sách này, gần như chắc chắn rằng thể loại thứ hai - giao diện người dùng phong phú chạy trên web (Web-based rich user interface) - là hướng đi được lựa chọn nhiều nhất và sẽ sớm chịu ảnh hưởng mạnh mẽ bởi HTML5. Các ứng dụng thuộc thể loại đầu tiên - giao diện web thuần request-response (yêu cầu - phản hồi) - có thể vẫn xuất hiện nhiều hơn dưới dạng các ứng dụng kế thừa (legacy applications) so với Web 2.0.

* Giao diện web thuần request-response, có lẽ được biết đến nhiều nhất với tên gọi Web 1.0. Các framework như Struts, Spring MVC, Spring Web Flow và ASP.NET hỗ trợ nhóm này.
* Giao diện ứng dụng Internet phong phú chạy trên nền web (RIA - Rich Internet Application), bao gồm cả những giao diện sử dụng DHTML và Ajax, thường được biết đến là Web 2.0. GWT của Google, YUI của Yahoo!, Ext JS, Flex của Adobe và Silverlight của Microsoft thuộc nhóm này.
* GUI (giao diện đồ họa) cho native client (ví dụ giao diện desktop trên Windows, Mac và Linux) có thể bao gồm việc sử dụng các thư viện trừu tượng (như Eclipse SWT, Java Swing, hoặc WinForms và WPF trên Windows). Điều này không nhất thiết ám chỉ một ứng dụng desktop nặng nề, dù điều đó hoàn toàn có thể xảy ra. GUI native client có thể truy cập các dịch vụ qua HTTP, ví dụ như thế, khiến cho giao diện người dùng trở thành thành phần duy nhất được cài đặt ở phía client.

Với bất kỳ danh mục giao diện người dùng nào kể trên, một vài câu hỏi ưu tiên cần phải được trả lời: Làm thế nào để chúng ta kết xuất các đối tượng miền lên màn hình ("onto the glass")? Và làm thế nào để truyền đạt các thao tác của người dùng trở lại cho mô hình?

> 💡 **Giải thích thêm:** Cụm từ "onto the glass" (nghĩa đen: lên mặt kính) là một cách nói lóng kỹ thuật thường được các kỹ sư phần mềm sử dụng để chỉ việc hiển thị dữ liệu trực quan lên màn hình thiết bị (màn hình máy tính, điện thoại, máy tính bảng). Trong ngữ cảnh thiết kế phần mềm và DDD, nó nhấn mạnh sự tách biệt giữa mô hình nghiệp vụ nội tại (domain model) và lớp hiển thị giao diện đồ họa mà người dùng nhìn thấy và tương tác.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

## Rendering Domain Objects

Có khá nhiều tranh cãi và bất đồng quan điểm về cách tốt nhất để kết xuất các đối tượng của domain model lên giao diện người dùng. Giao diện người dùng thường hưởng lợi từ các góc nhìn dữ liệu (views) phong phú hơn so với mức tối thiểu cần thiết để hoàn thành tác vụ trực tiếp. Việc hiển thị thêm dữ liệu là cần thiết vì nó cung cấp thông tin hỗ trợ mà người dùng cần để đưa ra các quyết định sáng suốt nhằm thực hiện nhiệm vụ trước mắt. Dữ liệu bổ sung cũng có thể bao gồm các tùy chọn để lựa chọn. Do đó, giao diện người dùng thường sẽ cần kết xuất các thuộc tính từ nhiều thực thể Aggregate (Chương 10). Điều này diễn ra bất chấp thực tế rằng trong phần lớn trường hợp, người dùng chỉ nên thực hiện một tác vụ thay đổi trạng thái (state-mutating task) áp dụng cho duy nhất một thực thể thuộc một loại Aggregate đơn lẻ. Tình huống này được minh họa trong Hình 14.2.

Figure 14.2 The user interface may need to render properties of multiple Aggregate instances but submit a request to modify only a single instance at a time.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000565_e23c78cd43286762a80039d854b9f148d1dcd1d569853819f536a3f17e542d09.png)

## Render Data Transfer Object from Aggregate Instances

Một phương pháp phổ biến để giải quyết bài toán kết xuất nhiều thực thể Aggregate vào một view duy nhất là sử dụng Data Transfer Object [Fowler, P of EAA], hay DTO (đối tượng truyền dữ liệu). DTO được thiết kế để chứa toàn bộ các thuộc tính cần hiển thị trong một view. Application Service (xem phần 'Application Services') sẽ sử dụng các Repository (Chương 12) để đọc các thực thể Aggregate cần thiết, sau đó ủy quyền cho một DTO Assembler [Fowler, P of EAA] (bộ lắp ráp DTO) để ánh xạ các thuộc tính vào DTO. Như vậy, DTO mang đầy đủ lượng thông tin cần kết xuất. Thành phần giao diện người dùng chỉ việc truy cập từng thuộc tính riêng lẻ của DTO và kết xuất nó lên view.

Với cách tiếp cận này, cả thao tác đọc và ghi đều được thực hiện thông qua Repository. Nó có ưu điểm là giải quyết được bất kỳ tập hợp dữ liệu nào được nạp trễ (lazy-loaded), bởi vì DTO Assembler sẽ truy cập trực tiếp vào mọi phần của Aggregate mà nó cần để tạo nên DTO. Nó cũng giải quyết được vấn đề cụ thể khi tầng trình diễn (presentation tier) bị tách rời về mặt vật lý khỏi tầng nghiệp vụ (business tier), và bạn cần tuần tự hóa (serialize) các vật chứa dữ liệu để truyền qua mạng tới tầng khác.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000566_c88a0275203207a3159155583fd849718f5c14288998f19d15cd33c13930e1bd.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000567_d438d414936d6f1c87e8beb59435ad7c8244bb97ab39ed71e2000ccae1339e37.png)

Thú vị thay, mẫu thiết kế DTO ban đầu được tạo ra để xử lý trường hợp tầng trình diễn nằm từ xa (remote presentation tier) tiếp nhận các thực thể DTO. DTO được xây dựng ở tầng nghiệp vụ, tuần tự hóa, gửi qua đường truyền mạng, và giải tuần tự hóa ở tầng trình diễn. Nếu tầng trình diễn của bạn không nằm ở xa, mẫu thiết kế này nhiều khi lại dẫn đến độ phức tạp ngẫu nhiên (accidental complexity) trong thiết kế ứng dụng, vi phạm nguyên lý YAGNI ("You Ain't Gonna Need It" - bạn sẽ không cần đến nó đâu). Nhược điểm này bao gồm việc đòi hỏi phải tạo ra các lớp mà đôi khi có hình thái rất giống với các đối tượng miền nhưng lại không hoàn toàn tương đồng. Nó cũng có mặt bất lợi là phải khởi tạo thêm các đối tượng tiềm ẩn kích thước lớn cần được quản lý bởi máy ảo (ví dụ JVM), trong khi thực tế chúng lại không hề phù hợp cho một kiến trúc ứng dụng chạy trên một máy ảo đơn lẻ.

Các Aggregate của bạn sẽ cần được thiết kế sao cho DTO Assembler có thể truy vấn các dữ liệu cần thiết. Hãy suy nghĩ cẩn trọng về cách bộc lộ trạng thái mà không để lộ quá nhiều về hình thái hoặc cấu trúc nội bộ của Aggregate. Hãy cố gắng loại bỏ sự liên kết chặt chẽ (coupling) của client đối với mọi thành phần bên trong của một Aggregate. Liệu bạn có nên cho phép client — trong trường hợp này là các Assembler — điều hướng sâu vào bên trong Aggregate hay không? Đó có thể là một ý tưởng tồi vì nó sẽ gắn kết chặt chẽ từng client với một triển khai cụ thể của Aggregate.

## Use a Mediator to Publish Aggregate Internal State

Để giải quyết vấn đề gắn kết chặt chẽ giữa mô hình và các client của nó, bạn có thể chọn thiết kế các interface theo mẫu Mediator [Gamma et al.] (mẫu thiết kế trung gian, còn được gọi là Double-Dispatch - cơ chế điều phối kép và Callback - hàm gọi lại) để Aggregate công khai trạng thái nội bộ của mình cho chúng. Các client sẽ triển khai interface Mediator, truyền tham chiếu đối tượng của lớp triển khai vào Aggregate dưới dạng một tham số của phương thức. Sau đó, Aggregate sẽ điều phối kép tới Mediator đó để công khai trạng thái được yêu cầu, toàn bộ quá trình này diễn ra mà không hề làm lộ hình thái hay cấu trúc của nó. Bí quyết ở đây là không ràng buộc interface của Mediator với bất kỳ loại đặc tả view nào, mà hãy giữ cho nó tập trung vào việc kết xuất các trạng thái mà Aggregate quan tâm:

```java
public class BacklogItem ... {
    ...
    public void provideBacklogItemInterest(
            BacklogItemInterest anInterest) {
        anInterest.informTenantId(this.tenantId().id());
        anInterest.informProductId(this.productId().id());
        anInterest.informBacklogItemId(this.backlogItemId().id());
        anInterest.informStory(this.story());
        anInterest.informSummary(this.summary());
        anInterest.informType(this.type().toString());
        ...
    }

```

```java
    public void provideTasksInterest(TasksInterest anInterest) {
        Set<Task> tasks = this.allTasks();
        anInterest.informTaskCount(tasks.size());
        for (Task task : tasks) {
            ...
        }
    }
    ...
}

```

Các bên cung cấp mối quan tâm (interest providers) khác nhau có thể được triển khai bởi các lớp khác, tương tự như cách mà các Entity (Chương 5) mô tả việc ủy quyền thẩm định (validation) cho các lớp validator riêng biệt.

Hãy lưu ý rằng một số người sẽ coi cách tiếp cận này hoàn toàn nằm ngoài phạm vi trách nhiệm của một Aggregate. Những người khác lại coi đó là một sự mở rộng hoàn toàn tự nhiên của một domain model được thiết kế tốt. Như mọi khi, những đánh đổi như vậy phải được các thành viên trong nhóm kỹ thuật của bạn thảo luận kỹ lưỡng.

## Render Aggregate Instances from a Domain Payload Object