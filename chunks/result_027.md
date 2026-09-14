![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000596_fdb9125e2dbe86ae3c0769de2ae2c7e08ea0023483afa9fcb94c63b044dfee06.png)

Khi tuần tự hóa (serialize) trạng thái hiện tại của một Aggregate (Cụm đối tượng nghiệp vụ) vào cơ sở dữ liệu, chúng ta luôn ghi đè lên trạng thái đã tuần tự hóa trước đó và không bao giờ có thể khôi phục lại được. Tuy nhiên, việc lưu giữ lý do dẫn đến từng thay đổi kể từ khi khởi tạo một thực thể (instance) Aggregate xuyên suốt toàn bộ vòng đời của nó lại có giá trị vô giá đối với doanh nghiệp. Như đã thảo luận trong Chương Kiến trúc (Architecture - Chương 4), những lợi ích mang lại có thể rất sâu rộng: độ tin cậy, thông tin nghiệp vụ thông minh (business intelligence) trong ngắn hạn và dài hạn, các khám phá phân tích dữ liệu, nhật ký kiểm toán (audit log) đầy đủ, và khả năng quay ngược thời gian để phục vụ mục đích gỡ lỗi (debugging).

- Bản chất chỉ ghi thêm (append-only) của các Event Stream (Luồng sự kiện) mang lại hiệu năng vượt trội và hỗ trợ hàng loạt tùy chọn sao chép dữ liệu (data replication). Việc áp dụng các phương pháp tương tự đã giúp những công ty như LMAX xây dựng các hệ thống giao dịch chứng khoán có độ trễ cực thấp (very low-latency).
- Cách tiếp cận lấy sự kiện làm trung tâm (Event-centric) trong thiết kế Aggregate cho phép các nhà phát triển tập trung nhiều hơn vào các hành vi được thể hiện thông qua Ngôn ngữ chung (Ubiquitous Language - Chương 1) nhờ việc tránh được sự bất tương thích trở kháng (impedance mismatch - sự lệch pha giữa mô hình đối tượng và cơ sở dữ liệu quan hệ) tiềm ẩn của cơ chế ánh xạ đối tượng - quan hệ (ORM - Object-Relational Mapping), đồng thời mang lại các hệ thống vững chắc hơn và thích ứng tốt hơn với sự thay đổi.

> 💡 **Giải thích thêm về "Impedance mismatch":**
> Khái niệm "Object-relational impedance mismatch" chỉ sự khác biệt căn bản giữa hai mô hình tư duy: mô hình lập trình hướng đối tượng (OOP) tập trung vào hành vi, đóng gói, đa hình và các mối quan hệ đồ thị; trong khi cơ sở dữ liệu quan hệ (RDBMS) lại dựa trên đại số quan hệ, các bảng hai chiều và khóa ngoại. Khi cố gắng ép các đối tượng nghiệp vụ phức tạp vào bảng CSDL, lập trình viên thường phải trả giá bằng hiệu năng và sự phức tạp của tầng ORM.
> (Nguồn tham khảo: https://martinfowler.com/bliki/OrmHate.html)

Dù vậy, chớ nên nhầm lẫn: A+ES (Aggregate + Event Sourcing - kết hợp Aggregate với Lưu trữ hướng sự kiện) không phải là một "viên đạn bạc" (silver bullet - giải pháp vạn năng giải quyết mọi vấn đề). Hãy cân nhắc một vài nhược điểm thực tế:

> 💡 **Giải thích thêm về "Silver bullet":**
> "Silver bullet" (viên đạn bạc) là thành ngữ bắt nguồn từ văn hóa dân gian (vũ khí duy nhất diệt được người sói), được Frederick Brooks đưa vào ngành công nghệ qua bài tiểu luận kinh điển *"No Silver Bullet — Essence and Accident in Software Engineering"* (1986). Thuật ngữ này ám chỉ một công nghệ hay kỹ thuật kỳ diệu có thể giải quyết dứt điểm mọi khó khăn trong phát triển phần mềm. Trong kỹ thuật phần mềm, không có giải pháp nào hoàn hảo cho mọi bài toán mà luôn đi kèm sự đánh đổi (trade-offs).
> (Nguồn tham khảo: https://en.wikipedia.org/wiki/No_Silver_Bullet)

- Việc định nghĩa các Event (Sự kiện) cho A+ES đòi hỏi sự thấu hiểu sâu sắc về miền nghiệp vụ (business domain). Như trong bất kỳ dự án DDD (Domain-Driven Design - Thiết kế hướng miền) nào, mức độ nỗ lực này thường chỉ xứng đáng đầu tư cho các mô hình phức tạp giúp tổ chức tạo ra lợi thế cạnh tranh.
- Tại thời điểm viết cuốn sách này, hệ thống công cụ (tooling) cũng như một hệ tri thức nhất quán trong lĩnh vực này vẫn còn thiếu hụt. Điều này làm gia tăng chi phí và rủi ro khi triển khai phương pháp tiếp cận này cho các nhóm phát triển chưa có nhiều kinh nghiệm.
- Số lượng lập trình viên có kinh nghiệm thực tế còn hạn chế.
- Việc triển khai A+ES gần như chắc chắn đòi hỏi phải áp dụng một hình thức nào đó của CQRS (Command-Query Responsibility Segregation - Tách biệt trách nhiệm giữa lệnh thay đổi và truy vấn - Chương 4), bởi các Event Stream rất khó để truy vấn trực tiếp. Điều này làm tăng gánh nặng nhận thức (cognitive load) và độ dốc đường cong học tập (learning curve) của nhà phát triển.

Với những ai không nản lòng trước các thách thức này, việc triển khai với A+ES có thể mang lại vô vàn lợi ích. Hãy cùng xem xét một số cách thức hiện thực hóa phương pháp tiếp cận mạnh mẽ này trong thế giới hướng đối tượng (object-oriented world).

## Bên trong một Application Service

Việc quan sát A+ES bên trong một Application Service (Dịch vụ ứng dụng - Chương 4, 14) sẽ giúp làm rõ bức tranh tổng thể. Thông thường, các Aggregate sẽ cư trú bên trong một mô hình miền (domain model), nằm phía sau các Application Service — vốn đóng vai trò là các client (bên gọi) trực tiếp của domain model.

Khi một Application Service nhận quyền điều khiển, nó sẽ tải một Aggregate và lấy ra bất kỳ Domain Service (Dịch vụ miền - Chương 7) hỗ trợ nào cần thiết cho nghiệp vụ của Aggregate đó. Khi Application Service ủy quyền cho nghiệp vụ của Aggregate thực thi, phương thức của Aggregate sẽ sinh ra các Event làm kết quả đầu ra. Những Event này làm thay đổi trạng thái (mutate state) của Aggregate, đồng thời cũng được xuất bản (publish) dưới dạng thông báo đến tất cả các bên đăng ký nhận tin (subscribers). Phương thức nghiệp vụ của Aggregate có thể yêu cầu truyền vào một hoặc nhiều Domain Service dưới dạng tham số. Việc sử dụng các Domain Service này có thể tính toán ra các giá trị tạo nên hiệu ứng phụ (side effects) tác động lên trạng thái của Aggregate. Một số thao tác của Domain Service như vậy có thể bao gồm việc gọi tới cổng thanh toán (payment gateway), yêu cầu cấp một định danh duy nhất (unique identity), hoặc truy vấn dữ liệu từ một hệ thống từ xa. Hình A.2 minh họa cách thức hoạt động này.

Hình A.2 Một Application Service kiểm soát việc truy cập và sử dụng Aggregate.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000597_84890c962fbf366354cf113b6b435af7bbe69052b83e5c7d6ebf53912222976a.png)

541

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000598_1feda9505e38e4050d29b2f88b9fe60c6a43413cf0bb92ce024c4c49844a40ee.png)

Đoạn mã Application Service triển khai bằng C# dưới đây minh họa cách thức hỗ trợ các bước trong Hình A.2:

```csharp
public class CustomerApplicationService 
{ 
    // event store for accessing event streams
    // (kho lưu trữ sự kiện để truy cập các luồng sự kiện)
    IEventStore _eventStore; 

    // domain service that is neeeded by aggregate
    // (dịch vụ miền cần thiết cho aggregate)
    IPricingService _pricingService; 

    // pass dependencies for this application service via constructor
    // (truyền các dependency cho application service này thông qua constructor)
    public CustomerApplicationService( 
        IEventStore eventStore, 
        IPricingService pricing) 
    { 
        _eventStore = eventStore; 
        _pricingService = pricing; 
    } 

    // Step 1: LockForAccountOverdraft method of 
    // Customer Application Service is called
    // (Bước 1: Phương thức LockForAccountOverdraft của Customer Application Service được gọi)
    public void LockForAccountOverdraft( 
        CustomerId customerId, 
        string comment) 
    { 
        // Step 2.1: Load event stream for Customer, given its id
        // (Bước 2.1: Tải event stream cho Customer dựa vào id)
        var stream = _eventStore.LoadEventStream(customerId); 

        // Step 2.2: Build aggregate from event stream
        // (Bước 2.2: Tái tạo aggregate từ event stream)
        var customer = new Customer(stream.Events); 

        // Step 3: Call aggregate method, passing it arguments and 
        // pricing domain service
        // (Bước 3: Gọi phương thức của aggregate, truyền vào các đối số và pricing domain service)
        customer.LockForAccountOverdraft(comment, _pricingService); 

        // Step 4: Commit changes to the event stream by id
        // (Bước 4: Commit các thay đổi vào event stream theo id)
        _eventStore.AppendToStream( 
            customerId, 
            stream.Version, 
            customer.Changes); 
    } 

    public void LockCustomer(CustomerId customerId, string reason) 
    { 
        var stream = _eventStore.LoadEventStream(customerId); 
        var customer = new Customer(stream.Events); 
        customer.Lock(reason); 
        _eventStore.AppendToStream( 
            customerId, 
            stream.Version, 
            customer.Changes); 
    } 

    // other methods on this application service
    // (các phương thức khác trên application service này)
}
```

`CustomerApplicationService` được khởi tạo cùng hai phụ thuộc (dependencies) thông qua constructor: `IEventStore` và `IPricingService`.

Khởi tạo thông qua constructor là một cách thức hợp lý để đáp ứng các dependency, nhưng chúng cũng hoàn toàn có thể được lấy ra thông qua một Service Factory (Nhà máy dịch vụ) hoặc sử dụng cơ chế Dependency Injection (Tiêm phụ thuộc). Tiêu chuẩn và quy ước thực hành của nhóm bạn sẽ quyết định điều này.

## Tôi Có Thể Tìm Mã Nguồn Mẫu Ở Đâu?

Toàn bộ mã nguồn cho các ví dụ về A+ES có sẵn để tải về tại đây: [http://lokad.github.com/lokad-iddd-sample/](http://lokad.github.com/lokad-iddd-sample/).

Giao diện `IEventStore` của chúng ta có thể có một định nghĩa đơn giản, và `EventStream` cũng tương tự như vậy:

```csharp
public interface IEventStore 
{ 
    EventStream LoadEventStream(IIdentity id); 
    EventStream LoadEventStream( 
        IIdentity id, 
        int skipEvents, 
        int maxCount); 
    void AppendToStream( 
        IIdentity id, 
        int expectedVersion, 
        ICollection<IEvent> events); 
} 

public class EventStream 
{ 
    // version of the event stream returned
    // (phiên bản của event stream được trả về)
    public int Version; 

    // all events in the stream
    // (toàn bộ các sự kiện trong stream)
    public List<IEvent> Events; 
}
```

Event Store này có thể được triển khai khá dễ dàng bằng một cơ sở dữ liệu quan hệ (Microsoft SQL, Oracle, hoặc MySQL) hoặc bằng một kho lưu trữ NoSQL có đảm bảo tính nhất quán mạnh (strong consistency) như hệ thống tệp tin (file system), MongoDB, RavenDB, hoặc Azure Blob storage.

Chúng ta tải các Event từ Event Store bằng định danh duy nhất (unique identity) của thực thể Aggregate cần được hoàn nguyên (reconstituted - tái tạo lại trạng thái). Hãy xem cách thực hiện điều này đối với một Aggregate có tên là `Customer`. Dù định danh duy nhất có thể thuộc bất kỳ kiểu dữ liệu nào, nhưng để tăng tính tường minh (expressiveness), chúng ta hãy sử dụng giao diện `IIdentity` được hiện thực hóa bởi `CustomerId`.

Chúng ta cần tải các Event thuộc về đối tượng `Customer` cụ thể đó, rồi truyền các Event này vào constructor của `Customer` để khởi tạo Aggregate:

```csharp
var eventStream = _eventStore.LoadEventStream(customerId); 
var customer = new Customer(eventStream.Events);
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000599_b70fcf59682b141b2128077102152245d4e4a1873b701ed66b2e4e634a00ae4a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000600_f5df346d084f1830f5b93fd384daf57b9499d5e66a2aa5f0220e1bb7349b75d6.png)

Như minh họa trong Hình A.3, Aggregate áp dụng các Event bằng cách phát lại (replaying) chúng qua phương thức `Mutate()`. Cách thức hoạt động như sau:

```csharp
public partial class Customer 
{ 
    public Customer(IEnumerable<IEvent> events) 
    { 
        // reinstate this aggregate to the latest version
        // (khôi phục aggregate này về phiên bản mới nhất)
        foreach (var @event in events) 
        { 
            Mutate(@event); 
        } 
    } 

    public bool ConsumptionLocked { get; private set; } 

    public void Mutate(IEvent e) 
    { 
        // .NET magic to call one of 'When' handlers with 
        // matching signature
        // (cơ chế linh hoạt của .NET để gọi handler 'When' có signature phù hợp)
        ((dynamic) this).When((dynamic)e); 
    } 

    public void When(CustomerLocked e) 
    { 
        ConsumptionLocked = true; 
    } 

    public void When(CustomerUnlocked e) 
    { 
        ConsumptionLocked = false; 
    } 
    // etc.
```

Hình A.3 Trạng thái của Aggregate được tái tạo lại bằng cách áp dụng các Event theo đúng thứ tự xảy ra.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000601_5d2ff394ec4c10c5da22cf6374a078176a1f1b84061b1e139cd1e7777f2d9fe6.png)

Phương thức `Mutate()` chỉ đơn thuần xác định (thông qua tính năng dynamic của .NET) phương thức nạp chồng `When()` tương ứng với kiểu tham số Event cụ thể, sau đó thực thi phương thức bằng cách truyền Event đó vào. Sau khi `Mutate()` hoàn tất, đối tượng `Customer` sẽ có trạng thái được hoàn nguyên hoàn toàn.

Chúng ta có thể tạo một thao tác truy vấn tái sử dụng được để tái tạo thực thể Aggregate từ Event Store:

```csharp
public Customer LoadCustomerById(CustomerId id) 
{ 
    var eventStream = _eventStore.LoadEventStream(id); 
    var customer = new Customer(eventStream.Events); 
    return customer; 
}
```

Sau khi xem xét cách một thực thể Aggregate có thể được hoàn nguyên từ một Luồng các Event trong lịch sử, chúng ta rất dễ hình dung ra các ứng dụng khác của bản ghi lịch sử này. Chúng ta có thể dùng chúng để nhìn lại quá khứ nhằm xem điều gì đã xảy ra và vào thời điểm nào. Khả năng quan sát này thậm chí còn trở nên mạnh mẽ hơn khi tính đến nhu cầu gỡ lỗi trên các hệ thống đang chạy thực tế (production deployments).

Các hoạt động nghiệp vụ được thực hiện như thế nào? Một khi Aggregate đã được tái tạo từ Event Store, Application Service sẽ ủy quyền cho một thao tác xử lý lệnh (command operation) trên thực thể Aggregate. Aggregate sẽ sử dụng trạng thái hiện tại cùng bất kỳ Domain Service nào mà hợp đồng (contract) yêu cầu để tiến hành thao tác. Khi một hành vi được thực thi, các thay đổi đối với trạng thái sẽ được biểu diễn dưới dạng các Event mới. Mỗi Event mới sẽ được chuyển tới phương thức `Apply()` của Aggregate, như được minh họa trong Hình A.4.

Hình A.4 Trạng thái của Aggregate dựa trên các Event trong quá khứ, và kết quả của hành vi sẽ sinh ra các Event mới.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000602_f96055058dda20b56a83ed7ce562d105519733dea2785c1204780db4f21b0f6e.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000603_03e6e5e165d9e25a80f5f8e96f058aab516f75f8a6914c61b6deda5d01f1c217.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000604_5290d2660c83c7637865d07ca178e1f4d3baed9c88b97d9f096b369af1df4bfe.png)

Như thấy trong đoạn mã sau, các Event mới được tích lũy vào tập hợp `Changes`, rồi sau đó được sử dụng để biến đổi (mutate) trạng thái hiện tại của Aggregate:

```csharp
public partial class Customer 
{ 
    ... 
    void Apply(IEvent @event) 
    { 
        // append event to change list for further persistence
        // (thêm event vào danh sách thay đổi để lưu trữ sau đó)
        Changes.Add(@event); 
        
        // pass each event to modify current in-memory state
        // (chuyển từng event vào để chỉnh sửa trạng thái hiện tại trong bộ nhớ)
        Mutate(@event); 
    } 
    ... 
}
```

Tất cả các Event được thêm vào tập hợp `Changes` sẽ được lưu trữ dưới dạng các bản ghi mới được ghi thêm vào cuối luồng. Vì mỗi Event cũng được dùng để thay đổi ngay lập tức trạng thái của Aggregate, nên nếu một hành vi có nhiều bước xử lý, mỗi bước tiếp theo đều có sẵn trạng thái mới nhất để thực hiện thao tác.

Tiếp theo, hãy xem xét một số hành vi nghiệp vụ của Aggregate `Customer`:

```csharp
public partial class Customer 
{ 
    // Second part of aggregate class
    // (Phần thứ hai của lớp aggregate)
    public List<IEvent> Changes = new List<IEvent>(); 

    public void LockForAccountOverdraft( 
        string comment, 
        IPricingService pricing) 
    { 
        if (!ManualBilling) 
        { 
            var balance = pricing.GetOverdraftThreshold(Currency); 
            if (Balance < balance) 
            { 
                LockCustomer("Overdraft. " + comment); 
            } 
        } 
    } 

    public void LockCustomer(string reason) 
    { 
        if (!ConsumptionLocked) 
        { 
            Apply(new CustomerLocked(_state.Id, reason)); 
        } 
    }
```

```csharp
    // Other business methods are not shown
    // (Các phương thức nghiệp vụ khác không được hiển thị)
    ... 
    void Apply(IEvent e) 
    { 
        Changes.Add(e); 
        Mutate(e); 
    } 
}
```

## Cân Nhắc Sử Dụng Hai Lớp Triển Khai

Để mã nguồn của bạn trở nên rõ ràng hơn, bạn có thể chia phần triển khai A+ES thành hai lớp riêng biệt: một lớp dành cho trạng thái (state) và một lớp dành cho hành vi (behavior), trong đó đối tượng trạng thái được giữ bởi đối tượng hành vi. Hai đối tượng này sẽ cộng tác với nhau duy nhất thông qua phương thức `Apply()`. Điều này đảm bảo rằng trạng thái chỉ bị biến đổi thông qua các Event.

Khi các hành vi làm thay đổi trạng thái hoàn tất, chúng ta phải commit tập hợp `Changes` vào Event Store. Chúng ta ghi thêm (append) tất cả các thay đổi mới, đồng thời đảm bảo không xảy ra xung đột đồng thời (concurrency conflict) với các luồng ghi khác. Việc kiểm tra này hoàn toàn khả thi vì chúng ta đã truyền một biến phiên bản đồng thời (concurrency version) từ phương thức `Load()` sang phương thức `Append()`.

Trong cách triển khai đơn giản nhất, sẽ có một tiến trình chạy ngầm (background processor) theo dõi kịp thời các Event mới được ghi thêm và xuất bản chúng tới một hạ tầng truyền thông điệp (messaging infrastructure - chẳng hạn như RabbitMQ, JMS, MSMQ, hoặc các hàng đợi đám mây), từ đó phân phối chúng tới tất cả các bên quan tâm. Xem Hình A.5.

Cách triển khai đơn giản này có thể được thay thế bằng các phương án phức tạp và tinh vi hơn. Một trong số đó là sao chép các Event ngay lập tức (immediately) hoặc cuối cùng (eventually) sang một hoặc nhiều bản sao (clones), nhằm tăng cường khả năng chịu lỗi (fault tolerance). Hình A.6 minh họa việc sao chép Event ngay lập tức sang một bản sao.

Hình A.5 Các Event mới được ghi thêm — kết quả từ hành vi của Aggregate — được xuất bản tới các bên đăng ký nhận tin.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000605_5f3ae5cc9e4968990a3c3cf3a3c557b666d1da997ef74abe27f4f8f844a471e8.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000606_4873fc09d644b76fc9cf04c2f42e517e26a07a6352f6b5a39530ada02d2aca89.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000607_c0059bfd8dbe314924dc1a55372fd921d891752fb9055aabdc58c6c106ff498b.png)

Hình A.6 Write-through: Một Master Event Store sao chép ngay lập tức tất cả các Event mới được thêm vào sang một Clone Event Store.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000608_7e3596ee153a1e4df67012123b447b5f235bdf6fe587395d92b9116b0fd9359f.png)

Trong trường hợp này, Master Event Store chỉ coi các Event của chính nó là đã được lưu sau khi nó sao chép thành công chúng sang Clone Event Store — đây chính là chiến lược ghi đồng bộ xuyên suốt (write-through).

Một giải pháp thay thế là sao chép các Event sang Clone sau khi các thay đổi đã được Master lưu lại bằng cách sử dụng một luồng (thread) riêng biệt — đây là chiến lược ghi hoãn lại (write-behind hay write-back). Cách tiếp cận này được minh họa trong Hình A.7. Trong trường hợp này, Clone có thể không nhất quán với Master, điều này đặc biệt dễ xảy ra nếu máy chủ gặp sự cố (crash) hoặc phân vùng mạng bị ảnh hưởng bởi độ trễ đường truyền.

> 💡 **Giải thích thêm về chiến lược "Write-through" và "Write-behind":**
> * **Write-through (Ghi đồng bộ):** Dữ liệu được ghi đồng thời vào cả bộ lưu trữ chính (Master) và bản sao dự phòng (Clone) trong cùng một giao dịch. Thao tác ghi chỉ được coi là thành công khi cả hai nơi đều đã ghi xong. Ưu điểm: Đảm bảo tính nhất quán dữ liệu cao và không bị mất mát khi có sự cố. Nhược điểm: Độ trễ (latency) của thao tác ghi cao hơn vì phụ thuộc vào tốc độ mạng và tốc độ ghi của node chậm nhất.
> * **Write-behind (Ghi hoãn lại / Bất đồng bộ):** Dữ liệu được xác nhận là ghi thành công ngay sau khi Master ghi xong; một tiến trình ngầm (asynchronous) sẽ chuyển tiếp dữ liệu đến Clone sau. Ưu điểm: Tốc độ phản hồi cực nhanh. Nhược điểm: Nguy cơ mất dữ liệu (data loss) hoặc dữ liệu bản sao bị cũ (stale) nếu Master bị sập trước khi kịp đồng bộ sang Clone.
> (Nguồn tham khảo: [https://en.wikipedia.org/wiki/Cache_(computing)#Writing_policies](https://en.wikipedia.org/wiki/Cache_(computing)#Writing_policies))

Để tóm tắt lại những gì đã được thảo luận từ đầu đến giờ, chúng ta hãy cùng điểm qua trình tự thực thi bắt đầu từ việc gọi một thao tác trên Application Service:

1. Client gọi một phương thức trên Application Service.
2. Lấy bất kỳ Domain Service nào cần thiết để thực hiện thao tác nghiệp vụ.
3. Dựa vào định danh thực thể Aggregate do client cung cấp, truy xuất Event Stream tương ứng của nó.

Hình A.7 Write-behind: Một Master Event Store sao chép bất đồng bộ (eventually) tất cả các Event mới được thêm vào sang một Clone Event Store.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000609_3289aac377534916406fac995ee565d7e1463a6fa7f95f1e535010b1952cf4e4.png)

4. Tái tạo thực thể Aggregate bằng cách áp dụng toàn bộ các Event từ Stream vào nó.
5. Thực thi thao tác nghiệp vụ do Aggregate cung cấp, truyền vào tất cả các tham số theo yêu cầu từ hợp đồng của giao diện.
6. Aggregate có thể thực hiện double-dispatch (cơ chế phân phối kép) tới bất kỳ Domain Service nào được cung cấp, tới các thực thể của những Aggregate khác, v.v., và sẽ sinh ra các Event mới làm kết quả đầu ra của thao tác.
7. Giả định rằng không có thao tác nghiệp vụ nào bị thất bại, ghi thêm tất cả các Event mới sinh vào Stream, sử dụng phiên bản của Stream (Stream version) để phòng ngừa các xung đột đồng thời.
8. Xuất bản các Event mới được ghi thêm từ Event Store tới các bên đăng ký nhận tin bằng cách sử dụng hạ tầng truyền thông điệp tùy chọn của bạn.

Chúng ta có thể nâng cấp phần triển khai A+ES bằng nhiều tùy chọn khác nhau. Ví dụ: chúng ta có thể sử dụng một Repository (Kho lưu trữ - Chương 12) để đóng gói quyền truy cập vào Event Store cũng như các chi tiết về việc tái tạo lại các thực thể Aggregate. Dựa trên các đoạn mã ở trên, bạn sẽ dễ dàng tạo ra một lớp cơ sở Repository có khả năng tái sử dụng. Giờ hãy cùng tập trung vào hai cải tiến tùy chọn đầy tính thực tế giúp ích rất nhiều cho các thiết kế A+ES: Command Handler (Bộ xử lý lệnh) và lambda.

## Command Handler

Hãy cùng xem xét những lợi thế của việc sử dụng Command (Lệnh - Chương 4, 14) và Command Handler để kiểm soát việc quản lý tác vụ trong ứng dụng của chúng ta. Để bắt đầu, trước tiên hãy nhìn lại Application Service và phương thức `LockCustomer()` của nó:

```csharp
public class CustomerApplicationService 
{ 
    ... 
    public void LockCustomer(CustomerId id, string reason) 
    { 
        var eventStream = _eventStore.LoadEventStream(id); 
        var customer = new Customer(stream.Events); 
        customer.LockCustomer(reason); 
        _store.AppendToStream(id, eventStream.Version, customer.Changes); 
    } 
    ... 
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000610_0ed900a11f595d83511fd499e681920a7753acb952fed9f36078356e85a503e7.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000611_48cabef86fc7a316b27858b9d159cbacc357d0e6f58cbf1dc4d526b7e0c01cb8.png)

Giờ hãy hình dung việc tạo ra một biểu diễn tuần tự hóa (serialized representation) của tên phương thức và các tham số của nó. Trông nó sẽ như thế nào? Chúng ta có thể tạo một lớp được đặt tên theo thao tác của ứng dụng và tạo các thuộc tính thực thể (instance properties) khớp với các tham số của phương thức dịch vụ. Lớp này sẽ tạo thành một Command:

```csharp
public sealed class LockCustomerCommand 
{ 
    public CustomerId { get; set; } 
    public string Reason { get; set; } 
}
```

Các hợp đồng Command tuân theo cùng ngữ nghĩa như Event và có thể được chia sẻ giữa các hệ thống theo cách thức tương tự. Command này sau đó có thể được truyền vào một phương thức trên Application Service:

```csharp
public class CustomerApplicationService 
{ 
    ... 
    public void When(LockCustomerCommand command) 
    { 
        var eventStream = _eventStore.LoadEventStream(command.CustomerId); 
        var customer = new Customer(stream.Events); 
        customer.LockCustomer(command.Reason); 
        _eventStore.AppendToStream( 
            command.CustomerId, 
            eventStream.Version, 
            customer.Changes); 
    } 
    ... 
}
```

Lần tái cấu trúc (refactoring) đơn giản này có thể mang lại một vài lợi ích lâu dài cho hệ thống. Hãy xem chúng hoạt động ra sao.

Vì các đối tượng Command có thể được tuần tự hóa, chúng ta có thể gửi các biểu diễn dạng văn bản hoặc nhị phân dưới dạng thông điệp (messages) qua một hàng đợi thông điệp (message queue). Đối tượng mà thông điệp được chuyển tới là một bộ xử lý thông điệp (message handler) và đối với chúng ta, đó chính là một Command Handler. Command Handler về mặt hiệu quả sẽ thay thế phương thức của Application Service, dù về cơ bản chúng tương đương nhau và vẫn có thể được gọi bằng tên đó. Dù sao đi nữa, việc tách rời (decoupling) client khỏi Service có thể tăng cường cân bằng tải (load balancing), kích hoạt mô hình các bên tiêu thụ cạnh tranh (competing consumers), và hỗ trợ phân vùng hệ thống (system partitioning). Lấy ví dụ về cân bằng tải: Chúng ta có thể san sẻ tải bằng cách khởi chạy cùng một Command Handler (về mặt ngữ nghĩa là một Application Service) trên bao nhiêu máy chủ tùy ý. Khi các Command được đưa vào message queue, các thông điệp Command có thể được phân phối tới một trong số nhiều Command Handler đang lắng nghe chúng. Điều này được mô tả trong Hình A.8. (Trong phụ lục này, các Command được thể hiện dưới dạng các đối tượng hình tròn.) Việc phân phối thực tế có thể được thực hiện bằng giải thuật round-robin (xoay vòng lần lượt) đơn giản hoặc một giải thuật phân phối phức tạp hơn, vốn đều được cung cấp sẵn bởi hạ tầng truyền thông điệp.

Hình A.8 Các Command của ứng dụng được phân phối tới nhiều Command Handler tùy ý

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000612_da7b1aa54501fb4645a7f72d7071557a3f66d78e55057f558ad89b256b4247b9.png)

Phương pháp này tạo ra sự tách rời về mặt thời gian (temporal decoupling) giữa các client và Application Service, hướng tới các hệ thống có tính bền bỉ cao hơn. Trước hết, client sẽ không còn bị nghẽn (blocked) nếu Application Service tạm thời không khả dụng trong một khoảng thời gian ngắn (ví dụ: để bảo trì hoặc nâng cấp). Thay vào đó, các Command sẽ được đưa vào một hàng đợi bền vững (persistent queue), nơi chúng sẽ được các Command Handler (Application Service) xử lý khi máy chủ của nó hoạt động trở lại, như được chỉ ra trong Hình A.9.

> 💡 **Giải thích thêm về "Temporal decoupling" (Tách rời về mặt thời gian):**
> Trong giao tiếp đồng bộ (synchronous), client và server bị ràng buộc chặt chẽ về thời gian: client gửi request và phải đợi phản hồi ngay lập tức; nếu server chết, request thất bại. Ngược lại, "temporal decoupling" (tách rời về thời gian) đạt được thông qua kiến trúc hướng thông điệp (message-driven). Client chỉ việc đẩy lệnh vào hàng đợi và tiếp tục công việc của mình mà không cần quan tâm server có đang chạy ngay tại tích tắc đó hay không. Message queue đảm bảo lệnh không bị mất và server sẽ xử lý khi sẵn sàng.
> (Nguồn tham khảo: https://en.wikipedia.org/wiki/Loose_coupling)

Một ưu điểm khác là khả năng xâu chuỗi (chain) các khía cạnh bổ sung (aspects) trước khi điều phối (dispatching) Command khi cần thiết. Chẳng hạn, chúng ta có thể dễ dàng gắn thêm (patch in) các tính năng như kiểm toán (auditing), ghi log (logging), ủy quyền (authorization), và xác thực dữ liệu (validation).

Hình A.9 Đặc tính tách rời về thời gian của các Command dựa trên thông điệp và Command Handler của chúng mang lại các tùy chọn sẵn sàng linh hoạt cho hệ thống.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000613_13fe37f9401b81f34e3d4d68ca9c6d89763d1d4c495822e483185773d21f4b99.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000614_0a726b9e95a6ad00e00946d08fe5e8b01861e5891c064f03f16343e0294eafe8.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000615_fcdb4a18a9fd9e62fda63d6d29b6cc85db0550ba57d7a0d3c21f26186f8dc33f.png)

Hãy xem xét cách chúng ta có thể gắn thêm tính năng ghi log. Trước tiên, chúng ta định nghĩa một giao diện chuẩn và triển khai giao diện đó trong một lớp Application Service:

```csharp
public interface IApplicationService 
{ 
    void Execute(ICommand cmd); 
} 

public partial class CustomerApplicationService : IApplicationService 
{ 
    public void Execute(ICommand command) 
    { 
        // pass command to a specific method When() 
        // that can handle the command
        // (chuyển command tới phương thức When() cụ thể có thể xử lý command đó)
        ((dynamic)this).When((dynamic)command); 
    } 
}
```

## Execute và Mutate Có Cách Triển Khai Tương Tự Nhau

Lưu ý rằng cách thức triển khai phương thức `Execute()` này có một số đặc điểm tương tự như phương thức `Mutate()` đã được mô tả trước đó trong thiết kế Aggregate theo A+ES.

Một khi chúng ta đã có một giao diện chuẩn cho tất cả các Command Handler (Application Service), chúng ta có thể gắn thêm bất kỳ tính năng tiêu chuẩn nào trước và sau khi thực thi (pre- and post-execution), chẳng hạn như việc ghi log tổng quát (generic logging):

```csharp
public class LoggingWrapper : IApplicationService 
{ 
    readonly IApplicationService _service; 

    public LoggingWrapper(IApplicationService service) 
    { 
        _service = service; 
    } 

    public void Execute(ICommand cmd) 
    { 
        Console.WriteLine("Command: " + cmd); 
        try 
        { 
            var watch = Stopwatch.StartNew(); 
            _service.Execute(cmd); 
            var ms = watch.ElapsedMilliseconds; 
            Console.WriteLine("  Completed in {0} ms", ms); 
        }
```

```csharp
        catch(Exception ex) 
        { 
            Console.WriteLine("Error: {0}", ex); 
        } 
    } 
}
```

Nhờ việc tất cả các Application Service đều tuân theo một giao diện chuẩn, chúng ta có thể gắn thêm bao nhiêu tiện ích chung tùy ý để chúng hoạt động trước và/hoặc sau các hàm xử lý thực tế của Command Handler. Dưới đây là cách khởi tạo `CustomerApplicationService` cùng với bộ ghi log trước và sau thực thi:

```csharp
var customerService = new CustomerApplicationService(eventStore, pricingService);
```

```csharp
var customerServiceWithLogging = new LoggingWrapper(customerService);
```

Tất nhiên, việc các Command là các đối tượng được tuần tự hóa và điều phối tới các Command Handler cho phép chúng ta xử lý nhiều sự cố và tình trạng lỗi khác nhau tại một vị trí duy nhất. Khi gặp một phân loại lỗi nhất định, chẳng hạn như tranh chấp tài nguyên do vấn đề đồng thời, chúng ta có thể lựa chọn một hành động phục hồi tiêu chuẩn, ví dụ thử lại (retry) thao tác đó X lần. Các lần thử lại có thể dựa trên chiến lược Capped Exponential Back-off (Độ trễ số mũ có giới hạn chặn trên), giúp cho tất cả các thao tác thử lại trở nên đồng nhất, đáng tin cậy và được duy trì bên trong một lớp duy nhất.

> 💡 **Giải thích thêm về "Capped Exponential Back-off":**
> Exponential Back-off là thuật toán giãn cách thời gian thử lại: sau mỗi lần thất bại, thời gian chờ sẽ tăng theo cấp số nhân (ví dụ: 100ms, 200ms, 400ms, 800ms...) để giảm áp lực dồn dập lên hệ thống đang quá tải. "Capped" nghĩa là đặt một giới hạn trần (ví dụ tối đa không quá 5 giây), tránh việc thời gian chờ tăng lên vô hạn khiến tiến trình bị treo quá lâu.
> (Nguồn tham khảo: [https://en.wikipedia.org/wiki/Exponential_backoff](https://en.wikipedia.org/wiki/Exponential_backoff))

## Cú Pháp Lambda

Nếu ngôn ngữ của bạn hỗ trợ các biểu thức lambda (lambda expressions), bạn hoàn toàn có thể thu gọn những đoạn mã vốn lặp đi lặp lại bằng cách tránh việc quản lý Event Stream một cách trùng lặp. Để chứng minh điều này, ở đây chúng ta giới thiệu một phương thức trợ giúp (helper method) bên trong Application Service:

```csharp
public class CustomerApplicationService 
{ 
    ... 
    public void Update(CustomerId id, Action<Customer> execute) 
    { 
        EventStream eventStream = _eventStore.LoadEventStream(id); 
        Customer customer = new Customer(eventStream.Events); 
        execute(customer); 
        _eventStore.AppendToStream( 
            id, 
            eventStream.Version, 
            customer.Changes); 
    } 
    ... 
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000616_1af63ebe06b924a8984d09872b2b495c261f602140ebb52e5dbb54e80ac52902.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000617_8d350d2b841aa23046cf90426f1481153959f5028ac7c289eaa4fded04779f59.png)

Trong phương thức này, tham số `Action<Customer> execute` tham chiếu tới một hàm ẩn danh (anonymous function - trong C# là một delegate) có thể thao tác trên bất kỳ thực thể `Customer` nào. Sự súc tích của biểu thức lambda có thể được nhận thấy qua tham số được truyền vào hàm `Update()`:

```csharp
public class CustomerApplicationService 
{ 
    ... 
    public void When(LockCustomer c) 
    { 
        Update(c.Id, customer => customer.LockCustomer(c.Reason)); 
    } 
    ... 
}
```

Trên thực tế, trình biên dịch C# sẽ tạo ra một đoạn mã tương tự như sau để hiện thực hóa ý đồ của biểu thức lambda:

```csharp
public class AnonymousClass_X 
{ 
    public string Reason; 
    public void Execute(Customer customer) 
    { 
        customer.LockCustomer(Reason); 
    } 
} 

public delegate void Action<T>(T argument); 

public void When(LockCustomer c) 
{ 
    var x = new AnonymousClass_X(); 
    x.Reason = c.Reason; 
    Update(c.Id, new Action<Customer>(customer => x.Execute(customer))); 
}
```

Vì hàm được sinh ra này nhận một thực thể `Customer` làm đối số, nó thực sự có thể được dùng để nắm bắt hành vi trong mã nguồn và thực thi hành vi đó nhiều lần trên các thực thể `Customer` khác nhau. Sức mạnh của việc sử dụng lambda sẽ được làm nổi bật trong phần tiếp theo.

## Kiểm Soát Đồng Thời

Các Event Stream của Aggregate có thể được truy cập và đọc bởi nhiều luồng (threads) cùng một lúc. Điều này mở ra khả năng thực tế về các xung đột đồng thời (concurrency conflicts) mà nếu không được kiểm soát, có thể dẫn đến hàng loạt trạng thái Aggregate không hợp lệ. Hãy xem xét tình huống khi hai luồng cùng cố gắng chỉnh sửa Event Stream tại cùng một thời điểm, như được thể hiện trong Hình A.10.

Hình A.10 Hai luồng tranh chấp cùng một thực thể của một Aggregate được thiết kế theo mô hình A+ES

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000618_88a375d4c9350c1717bf158ee8fae90c52e759bc76a9032edebf6f9610531737.png)

Cách giải quyết đơn giản nhất cho tình huống này là ném ra ngoại lệ `EventStoreConcurrencyException` ở bước 4, cho phép nó lan truyền (propagate) ngược lên đến tận client cuối cùng:

```csharp
public class EventStoreConcurrencyException : Exception 
{ 
    public List<IEvent> StoreEvents { get; set; } 
    public long StoreVersion { get; set; } 
}
```

Khi bắt được ngoại lệ này ở client cuối cùng, người dùng có thể sẽ được hướng dẫn thử lại thao tác theo cách thủ công.

Thay vì áp dụng cách tiếp cận đó ngay từ đầu, bạn có lẽ sẽ đồng ý rằng một phương pháp thử lại chuẩn hóa sẽ là tối ưu nhất. Vì vậy, khi Event Store của chúng ta ném ra ngoại lệ `EventStoreConcurrencyException`, chúng ta có thể lập tức thử phục hồi:

```csharp
void Update(CustomerId id, Action<Customer> execute) 
{ 
    while(true) 
    {
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000619_f8ba902a45a166fd4ae62c4acd7e79b0f57d9c3f5d7739d3b1840ce3f214f95c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000620_e690f53bb5dc6673d35dbe1e3f92e3d4668556a46140a52cc45445c3a99b30aa.png)

```csharp
        EventStream eventStream = _eventStore.LoadEventStream(c.Id); 
        var customer = new Customer(eventStream.Events); 
        try 
        { 
            execute(customer); 
            _eventStore.AppendToStream( 
                c.Id, 
                eventStream.Version, 
                customer.Changes); 
            return; 
        } 
        catch (EventStoreConcurrencyException) 
        { 
            // fall through and retry, with optional brief delay
            // (bỏ qua và thử lại, có thể kèm khoảng trễ ngắn tùy chọn)
        } 
    } 
}
```

Trong trường hợp xung đột đồng thời xảy ra, chúng ta sẽ thêm các bước bổ sung sau để khắc phục vấn đề:

1. Luồng 2 (Thread 2) bắt ngoại lệ và đi tiếp, chuyển quyền điều khiển trở lại đầu vòng lặp `while`. Lúc này, các Event từ 1 đến 5 được tải vào một thực thể `Customer` mới.
2. Luồng 2 thực thi lại delegate trên đối tượng `Customer` vừa được tải lại, và thao tác này giờ đây sẽ sinh ra các Event 6-7; các Event này sau đó sẽ được ghi thêm thành công vào sau Event 5.

Nếu việc thực thi lại hành vi của Aggregate quá tốn kém hoặc vì lý do nào đó mà không khả thi (ví dụ: đòi hỏi phải tích hợp tốn chi phí với hệ thống của bên thứ ba để đặt hàng hoặc quẹt thẻ tín dụng), chúng ta có thể muốn sử dụng một chiến lược khác.

Như được minh họa trong Hình A.11, một chiến lược như vậy là giải quyết xung đột Event (Event conflict resolution), vốn được sử dụng để giảm bớt số lượng ngoại lệ đồng thời thực tế. Dưới đây là cách hoạt động của một trường hợp giải quyết xung đột rất đơn giản:

Hình A.11 Sử dụng giải quyết xung đột Event trên Event Stream của một Aggregate

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000621_8286799c0249226699ca660a20d068e566b3f76d18fe9368e15dc0e8effccf4e.png)

```csharp
void UpdateWithSimpleConflictResolution( 
    CustomerId id, 
    Action<Customer> execute) 
{ 
    while (true) 
    { 
        EventStream eventStream = _eventStore.LoadEventStream(id); 
        Customer customer = new Customer(eventStream.Events); 
        execute(customer); 
        try 
        { 
            _eventStore.AppendToStream( 
                id, 
                eventStream.Version, 
                customer.Changes); 
            return; 
        } 
        catch (EventStoreConcurrencyException ex) 
        { 
            foreach (var failedEvent in customer.Changes) 
            { 
                foreach (var succeededEvent in ex.ActualEvents) 
                { 
                    if (ConflictsWith(failedEvent, succeededEvent)) 
                    { 
                        var msg = string.Format(
                            "Conflict between {0} and {1}", 
                            failedEvent, 
                            succeededEvent); 
                        throw new RealConcurrencyException(msg, ex); 
                    } 
                } 
            } 
            // there are no conflicts and we can append
            // (không có xung đột và chúng ta có thể ghi thêm)
            _eventStore.AppendToStream( 
                id, 
                ex.ActualVersion, 
                customer.Changes); 
        } 
    } 
}
```

Trong trường hợp này, phương thức phát hiện xung đột `ConflictsWith()` được sử dụng để so sánh từng Event của Aggregate nhằm tìm kiếm xung đột với các Event đã được ghi đồng thời vào Event Store (như được báo cáo trong ngoại lệ).

Phương thức giải quyết xung đột này thường được định nghĩa riêng cho từng Aggregate Root (Gốc cụm đối tượng nghiệp vụ), tùy thuộc vào các loại hành vi cụ thể mà nó hỗ trợ. Dù vậy, vẫn có một cách triển khai `ConflictsWith()` có thể hoạt động tốt cho phần lớn các Aggregate:

```csharp
bool ConflictsWith(IEvent event1, IEvent event2) 
{ 
    return event1.GetType() == event2.GetType(); 
}
```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000622_1775c96bbfcb852b779a53440ad8e86c5660237239438741aa5d9bc016a3a1fc.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000623_97633ffc504f95f5da96cd70f5e98ace5b27e7d65327ac873737a399f1091105.png)

Việc giải quyết xung đột cho phần lớn các trường hợp này dựa trên một quy tắc đơn giản: Các Event cùng loại luôn xung đột với nhau, nhưng các Event khác loại thì không.

## Sự Tự Do Về Mặt Cấu Trúc Với A+ES

Một trong những lợi thế thực tiễn lớn nhất của A+ES là sự đơn giản trong việc lưu trữ bền vững (persistence) và tính linh hoạt mà nó đem lại. Cho dù cấu trúc của một Aggregate phức tạp đến đâu, nó luôn có thể được biểu diễn bằng một chuỗi các Event đã được tuần tự hóa dùng để hoàn nguyên trạng thái của nó. Nhiều miền nghiệp vụ tác động làm thay đổi mô hình theo thời gian, kéo theo các hành vi mới hoặc các nét tinh tế trong mô hình hóa phát sinh từ các yêu cầu liên tục thay đổi của một hệ thống đang phát triển. Ngay cả khi chúng ta buộc phải tái cấu trúc việc triển khai nội bộ của một Aggregate nhất định để đáp ứng các thay đổi quan trọng, A+ES hầu như luôn có thể tạo điều kiện thuận lợi cho những thay đổi đó với rủi ro thấp hơn cùng sự nhẹ nhàng, không gây ức chế cho các nhà phát triển.

Chuỗi các Event gắn liền với một định danh cụ thể thường được gọi là một Event Stream. Về bản chất, nó chỉ là một danh sách các thông điệp chỉ cho phép ghi thêm (append-only) được tuần tự hóa thành các khối byte bằng bộ tuần tự hóa tùy chọn của bạn. Nhờ vậy, một Event Stream có thể được lưu trữ bền vững với hiệu quả tương đương nhau dù sử dụng cơ sở dữ liệu quan hệ, cơ sở dữ liệu NoSQL, hệ thống tệp tin thông thường, hay lưu trữ đám mây, miễn là kho lưu trữ được lựa chọn có đảm bảo tính nhất quán mạnh (strong consistency guarantees).

Dưới đây là ba ưu điểm lớn của việc lưu trữ theo A+ES, đặc biệt quan trọng đối với các Bounded Context (Ngữ cảnh bị giới hạn - Chương 2) có vòng đời dài:

* Khả năng điều chỉnh cách triển khai nội bộ của một Aggregate theo bất kỳ biểu diễn cấu trúc thực tế nào cần thiết để thể hiện các hành vi mới mà các chuyên gia nghiệp vụ (domain experts) phát hiện ra.
* Khả năng dịch chuyển toàn bộ hạ tầng giữa các giải pháp lưu trữ (hosting) khác nhau, giúp chúng ta chủ động đối phó với sự cố gián đoạn dịch vụ đám mây (cloud outages) và cung cấp các phương án chuyển đổi dự phòng (fail-over) vững chắc.
* Khả năng cho phép tải Event Stream của bất kỳ thực thể Aggregate nào về máy tính phát triển và phát lại để gỡ lỗi một tình trạng lỗi cụ thể.

## Hiệu Năng

Đôi khi, việc tải các Aggregate từ các Stream có kích thước lớn có thể gây ra các vấn đề về hiệu năng, đặc biệt là khi các Stream riêng lẻ vượt quá hàng trăm nghìn Event. Có một vài mẫu (patterns) đơn giản có thể được áp dụng trong từng trường hợp riêng biệt để giải quyết bài toán này:

Hình A.12 Một Event Stream của Aggregate với một bản chụp nhanh (snapshot) trạng thái của nó, theo sau là hai Event xảy ra sau khi bản chụp nhanh được tạo

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000624_a1d047024c5530ed257b5fa2cdd33b3d275c3f4ca99cb278431cd0c63fb16671.png)

* Lưu bộ nhớ đệm (cache) các Event Stream trong bộ nhớ máy chủ (server memory), tận dụng lợi thế rằng các Event là bất biến (immutable) một khi đã được ghi vào Event Store. Khi truy vấn Event Store để tìm bất kỳ thay đổi nào, chúng ta có thể cung cấp phiên bản của Event được biết gần nhất và chỉ yêu cầu lấy những Event xảy ra kể từ thời điểm đó (nếu có). Cách này có thể cải thiện hiệu năng nhưng sẽ phải đánh đổi bằng mức tiêu tốn dung lượng bộ nhớ.
* Tránh việc phải tải và phát lại một phần lớn của Event Stream bằng cách chụp nhanh (snapshot) từng thực thể Aggregate. Bằng cách này, khi tải bất kỳ thực thể Aggregate nào, bạn chỉ cần tìm bản chụp nhanh mới nhất của nó, sau đó chỉ phát lại các Event đã được ghi thêm vào Event Stream kể từ khi bản chụp nhanh đó được tạo.

Như minh họa trong Hình A.12, các snapshot thực chất chỉ là các bản sao tuần tự hóa toàn bộ trạng thái của Aggregate, được chụp tại những thời điểm nhất định, và nằm trong Event Stream dưới dạng các phiên bản cụ thể. Chúng có thể được lưu trữ bền vững trong một Repository được đóng gói phía sau một giao diện đơn giản như sau:

```csharp
public interface ISnapshotRepository 
{ 
    bool TryGetSnapshotById<TAggregate>( 
        IIdentity id, 
        out TAggregate snapshot, 
        out int version); 
    void SaveSnapshot( 
        IIdentity id, 
        TAggregate snapshot, 
        int version); 
}
```

Chúng ta phải lưu lại phiên bản của Stream cùng với mỗi snapshot. Dựa vào số phiên bản này, chúng ta có thể tải snapshot cùng với chỉ những Event xảy ra kể từ thời điểm snapshot đó được ghi nhận. Ban đầu, chúng ta lấy snapshot làm trạng thái cơ sở (base state) của thực thể Aggregate, sau đó tải và phát lại toàn bộ các Event phát sinh kể từ khi snapshot được chụp:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000625_226cb2f4aa366aa76e3837434853cc1624dcecfffc42f8e0c21e9d2273d5477a.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000626_a7881cb4993b908e83eb8d9b123907baf1974ba60deca459eb5ec9c4fe3cd0f0.png)

```csharp
// our event store
// (kho lưu trữ sự kiện của chúng ta)
IEventStore _store; 

public Customer LoadCustomerAggregateById(CustomerId id) 
{ 
    Customer customer; 
    long snapshotVersion = 0; 

    if (_snapshots.TryGetSnapshotById( 
        id, 
        out customer, 
        out snapshotVersion)) 
    { 
        // load any events since snapshot was taken
        // (tải các sự kiện phát sinh kể từ khi snapshot được chụp)
        EventStream stream = _store.LoadEventStreamAfterVersion( 
            id, 
            snapshotVersion); 

        // replay these events to update snapshot
        // (phát lại các sự kiện này để cập nhật snapshot)
        customer.ReplayEvents(stream.Events); 
        return customer; 
    } 
    else // we don't have any persisted snapshot
         // (chúng ta chưa có snapshot nào được lưu trữ)
    { 
        EventStream stream = _store.LoadEventStream(id); 
        return new Customer(stream.Events); 
    } 
}
```

Phương thức `ReplayEvents()` phải được sử dụng để đưa trạng thái thực thể Aggregate về phiên bản mới nhất với các Event xảy ra kể từ snapshot gần nhất. Hãy nhớ rằng trạng thái thực thể Aggregate được làm thay đổi tính từ thời điểm snapshot mới nhất trở đi. Do đó, chúng ta sẽ không khởi tạo `Customer` (trong ví dụ này) chỉ bằng Event Stream đơn thuần. Chúng ta cũng không thể chỉ sử dụng `Apply()`, bởi vì nó không những làm thay đổi trạng thái hiện tại với Event được đưa vào mà còn lưu từng Event mà nó nhận được vào tập hợp `Changes`. Việc lưu vào `Changes` những Event vốn đã tồn tại sẵn trong Event Stream sẽ gây ra các lỗi nghiêm trọng. Vì vậy, chúng ta chỉ cần triển khai thêm phương thức mới `ReplayEvents()`:

```csharp
public partial class Customer 
{ 
    ... 
    public void ReplayEvents(IEnumerable<IEvent> events) 
    { 
        foreach (var @event in events) 
        { 
            Mutate(@event); 
        } 
    } 
    ... 
}
```

Hình A.13 Bản chụp nhanh của một Aggregate được sinh ra sau khi một số lượng Event mới nhất định xuất hiện.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000627_f1642dde88e77562ec3f7f7639413f8a31bc06a3f27e382db72ec13aa8110a71.png)

Dưới đây là đoạn mã đơn giản để sinh các snapshot cho `Customer`:

```csharp
public void GenerateSnapshotForCustomer(IIdentity id) 
{ 
    // load all events from the start
    // (tải toàn bộ sự kiện từ ban đầu)
    EventStream stream = _store.LoadEventStream(id); 
    Customer customer = new Customer(stream.Events); 
    _snapshots.SaveSnapshot(id, customer, stream.Version); 
}
```

Việc sinh và lưu trữ snapshot có thể được ủy thác cho một luồng chạy nền (background thread). Các snapshot mới sẽ chỉ được tạo ra sau khi một số lượng Event định trước xuất hiện tính từ snapshot mới nhất. Các bước này được biểu thị trong Hình A.13. Vì đặc tính của từng loại Aggregate có thể rất khác nhau, nên ngưỡng kích hoạt chụp snapshot cho từng loại có thể được tinh chỉnh để đáp ứng các nhu cầu hiệu năng cụ thể.

Một cách bổ sung khác để xử lý các mối lo ngại về hiệu năng đối với các Aggregate A+ES là phân vùng (partition) các Aggregate trên nhiều tiến trình hoặc nhiều máy chủ dựa vào định danh của Aggregate. Việc phân vùng này có thể được thực hiện bằng cách băm định danh (identity hashing) hoặc các thuật toán khác, đồng thời có thể kết hợp với cả việc lưu bộ nhớ đệm thực thể Aggregate và snapshot của Aggregate.

## Triển Khai Một Event Store

Bây giờ, chúng ta hãy cùng bắt tay vào triển khai một vài Event Store khác nhau phù hợp để sử dụng với A+ES. Các Store ở đây tương đối đơn giản và không được thiết kế cho hiệu năng cực cao, nhưng chúng sẽ đủ tốt cho hầu hết các miền nghiệp vụ.

Mặc dù phần triển khai chi tiết cho từng Event Store có sự khác nhau, nhưng các hợp đồng (contracts/interfaces) của chúng là như nhau:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000628_f34dca0caf247209acf40ec1d0c2f1db0e8181497ee32dc7cf0d900ad5a840ef.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000629_94b53b1e1b481cddb8ca2337076a146311f0104690f33bf7ed1991134571bcab.png)

```csharp
public interface IEventStore 
{ 
    // loads all events for a stream
    // (tải toàn bộ các sự kiện cho một stream)
    EventStream LoadEventStream(IIdentity id); 

    // loads subset of events for a stream
    // (tải một tập con các sự kiện cho một stream)
    EventStream LoadEventStream( 
        IIdentity id, 
        int skipEvents, 
        int maxCount); 

    // appends events to a stream, throwing 
    // OptimisticConcurrencyException another appended 
    // new events since expectedversion
    // (ghi thêm các sự kiện vào stream, ném ra 
    // OptimisticConcurrencyException nếu có luồng khác đã ghi thêm
    // sự kiện mới kể từ expectedVersion)
    void AppendToStream( 
        IIdentity id, 
        int expectedVersion, 
        ICollection<IEvent> events); 
} 

public class EventStream 
{ 
    // version of the event stream returned
    // (phiên bản của event stream được trả về)
    public int Version; 

    // all events in the stream
    // (toàn bộ các sự kiện trong stream)
    public IList<IEvent> Events = new List<IEvent>(); 
}
```

Như minh họa trong Hình A.14, lớp triển khai `IEventStore` là một vỏ bọc (wrapper) mang tính đặc thù của dự án bao quanh `IAppendOnlyStore` vốn mang tính tổng quát và có khả năng tái sử dụng cao hơn. Trong khi việc triển khai `IEventStore` xử lý việc tuần tự hóa và định kiểu dữ liệu mạnh (strong typing), thì các triển khai của `IAppendOnlyStore` lại cung cấp quyền truy cập cấp thấp (low-level) tới nhiều cơ chế lưu trữ (storage engines) khác nhau.

Hình A.14 Các đặc tính của IEventStore cấp cao hơn và IAppendOnlyStore cấp thấp hơn

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000630_dce6a5f79a6c6a48a1c1a9b200a6ad3a8dd892e77e9b7631e74082a8a2aa0979.png)

## Mã Nguồn Của Event Store

Mã nguồn đầy đủ cho nhiều loại Event Store với các phương án lưu trữ khác nhau có sẵn để tải về dưới dạng một phần của dự án mẫu A+ES: [http://lokad.github.com/lokad-iddd-sample/](http://lokad.github.com/lokad-iddd-sample/).

Dưới đây là giao diện `IAppendOnlyStore` ở cấp thấp hơn:

```csharp
public interface IAppendOnlyStore : IDisposable 
{ 
    void Append(string name, byte[] data, int expectedVersion = -1); 
    IEnumerable<DataWithVersion> ReadRecords( 
        string name, 
        int afterVersion, 
        int maxCount); 
    IEnumerable<DataWithName> ReadRecords( 
        int afterVersion, 
        int maxCount); 
    void Close(); 
} 

public class DataWithVersion 
{ 
    public int Version; 
    public byte[] Data; 
} 

public sealed class DataWithName 
{ 
    public string Name; 
    public byte[] Data; 
}
```

Như bạn có thể thấy, `IAppendOnlyStore` làm việc với các mảng byte thay vì các tập hợp Event, và sử dụng chuỗi tên (string names) thay vì các định danh có định kiểu mạnh. Lớp `EventStore` sẽ đảm nhận việc chuyển đổi qua lại giữa hai dạng dữ liệu này.

`IAppendOnlyStore` khai báo hai phương thức `ReadRecords()` riêng biệt. Phương thức đầu tiên được sử dụng để đọc các Event bên trong một Stream đơn lẻ dựa trên tên của chúng, và phương thức thứ hai dùng để đọc toàn bộ các Event có trong Store. Cả hai phương thức triển khai đều phải luôn đọc các Event theo đúng thứ tự mà chúng đã được lưu trữ bền vững. Như bạn có thể đã suy luận, phương thức nạp chồng đầu tiên là cần thiết để xây dựng lại trạng thái của một Aggregate đơn lẻ. Phương thức `ReadRecords()` thứ hai được tầng hạ tầng sử dụng để sao chép các Event, xuất bản chúng mà không cần đến cơ chế commit hai pha (two-phase commit), cũng như xây dựng lại các mô hình đọc bền vững (persistent read models) như những gì cần thiết cho các giao diện người dùng dựa trên CQRS.

> 💡 **Giải thích thêm về "Two-phase commit (2PC)":**
> Giao thức commit hai pha (2PC) là một thuật toán đồng thuận trong hệ thống phân tán, dùng để đảm bảo tính toàn vẹn nguyên tử (atomic) khi ghi dữ liệu đồng thời vào nhiều hệ thống khác nhau (ví dụ: vừa ghi vào DB vừa đẩy message vào Message Queue). 2PC thường có độ trễ cao và dễ gây tắc nghẽn (blocking). Bằng cách lưu Event vào Store trước rồi dùng một tiến trình riêng đọc Event ra để publish (mẫu hình Transactional Outbox / Event Tailing), hệ thống tránh hoàn toàn được sự phức tạp và chậm chạp của 2PC.
> (Nguồn tham khảo: [https://en.wikipedia.org/wiki/Two-phase_commit_protocol](https://en.wikipedia.org/wiki/Two-phase_commit_protocol))

Một cách tiếp cận đơn giản cho việc tuần tự hóa (serialization) và giải tuần tự hóa (deserialization) — tức chuyển đổi giữa các mảng byte và các đối tượng Event được định kiểu mạnh — là sử dụng `BinaryFormatter` của .NET:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000631_2f4c110a279283394e29d0e5c681c311e76534f4c5b0cc4a50923dd84a608a7f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000632_20711ff671186f0a26e480b9dd408611f40ab4a12dc25f7292f7e0aaf3b460fd.png)

## Phụ lục A AGGREGATE VÀ EVENT SOURCING: A+ES

```csharp
public class EventStore : IEventStore 
{ 
    readonly BinaryFormatter _formatter = new BinaryFormatter(); 

    byte[] SerializeEvent(IEvent[] e) 
    { 
        using (var mem = new MemoryStream()) 
        { 
            _formatter.Serialize(mem, e); 
            return mem.ToArray(); 
        } 
    } 

    IEvent[] DeserializeEvent(byte[] data) 
    { 
        using (var mem = new MemoryStream(data)) 
        { 
            return (IEvent[])_formatter.Deserialize(mem); 
        } 
    } 
}
```

Dưới đây là cách chúng ta có thể sử dụng tuần tự hóa và giải tuần tự hóa để tải một Event Stream:

```csharp
readonly IAppendOnlyStore _appendOnlyStore; 
... 
public EventStream LoadEventStream(IIdentity id, int skip, int take) 
{ 
    var name = IdentityToString(id); 
    var records = _appendOnlyStore.ReadRecords(name, skip, take).ToList(); 
    var stream = new EventStream(); 
    foreach (var tapeRecord in records) 
    { 
        stream.Events.AddRange(DeserializeEvent(tapeRecord.Data)); 
        stream.Version = tapeRecord.Version; 
    } 
    return stream; 
} 

string IdentityToString(IIdentity id) 
{ 
    // in this project all identities produce proper name
    // (trong dự án này tất cả các identity đều tạo ra tên phù hợp)
    return id.ToString(); 
}
```

Ở đây chúng ta thấy cách ghi thêm các Event mới vào Event Store thông qua `IAppendOnlyStore`:

```csharp
public void AppendToStream( 
    IIdentity id, 
    int originalVersion, 
    ICollection<IEvent> events) 
{ 
    if (events.Count == 0) return; 

    var name = IdentityToString(id); 
    var data = SerializeEvent(events.ToArray()); 
    try 
    { 
        _appendOnlyStore.Append(name, data, originalVersion); 
    } 
    catch(AppendOnlyStoreConcurrencyException e) 
    { 
        // load server events
        // (tải các sự kiện từ máy chủ)
        var server = LoadEventStream(id, 0, int.MaxValue); 

        // throw a real problem
        // (ném ra ngoại lệ về sự cố thực sự)
        throw OptimisticConcurrencyException.Create( 
            server.Version, 
            e.ExpectedVersion, 
            id, 
            server.Events); 
    } 
}
```

## Lưu Trữ Dưới Dạng Quan Hệ

Các khả năng và sự đảm bảo tính nhất quán mạnh mẽ mà cơ sở dữ liệu quan hệ mang lại tạo nên cách tiếp cận đơn giản nhất để triển khai việc lưu trữ chỉ ghi thêm (append-only persistence). Thực tế là nhiều doanh nghiệp đã tiêu chuẩn hóa một hoặc nhiều sản phẩm cơ sở dữ liệu quan hệ, đồng nghĩa với việc sẽ tốn rất ít hoặc hầu như không mất chi phí hay thời gian làm quen khi sử dụng chúng làm Event Store.

Vì cơ sở dữ liệu MySQL là một máy chủ cơ sở dữ liệu quan hệ mã nguồn mở phổ biến hiện diện trên nhiều nền tảng, chúng ta sẽ sử dụng nó để triển khai một Event Store. Lớp `MySQLAppendOnlyStore` triển khai giao diện `IAppendOnlyStore`, đóng vai trò như một tầng truy cập. Nó sẽ được dùng để lưu các Event dưới dạng dữ liệu nhị phân vào bảng `ES_Events`, và sau đó tải lại các Event đã được lưu trữ bền vững đó.

Dưới đây là định nghĩa bảng quản lý Event Stream cho từng loại Aggregate trong một Bounded Context:

```sql
CREATE TABLE IF NOT EXISTS `ES_Events` ( 
    `Id` int NOT NULL AUTO_INCREMENT,        -- unique id (id duy nhất)
    `Name` nvarchar(50) NOT NULL,            -- name of the stream (tên của stream)

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000633_bc2fdc23683ea0679ed80544250ec0b1d9107f0db867b929320a136e1c2e12c5.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000634_72389723e94b72ffd55a0b07f6d03c303706ae41dbda0ad94dbd511a9fa20077.png)

`Version` int NOT NULL,                  -- incrementing stream version (phiên bản tăng dần của stream)

```sql
`Data` LONGBLOB NOT NULL                 -- data payload (nội dung tải dữ liệu)

```

)

Để ghi thêm một Event vào một Stream cụ thể bằng cách sử dụng một transaction (giao dịch), hãy thực hiện các bước sau:

1. Bắt đầu một transaction.
2. Kiểm tra xem Event Store có bị thay đổi so với phiên bản dự kiến (expected version) hay không; nếu có, ném ra ngoại lệ.
3. Nếu không có xung đột đồng thời, ghi thêm các Event.
4. Commit transaction.

Dưới đây là mã nguồn cho phương thức `Append()`:

```csharp
public void Append(string name, byte[] data, int expectedVersion) 
{ 
    using (var conn = new MySqlConnection(_connectionString)) 
    { 
        conn.Open(); 
        using (var tx = conn.BeginTransaction()) 
        { 
            const string sql = @"SELECT COALESCE(MAX(Version),0) FROM `ES_Events` WHERE Name=?name"; 
            int version; 
            using (var cmd = new MySqlCommand(sql, conn, tx)) 
            { 
                cmd.Parameters.AddWithValue("?name", name); 
                version = (int)cmd.ExecuteScalar(); 
                if (expectedVersion != -1) 
                { 
                    if (version != expectedVersion) 
                    { 
                        throw new AppendOnlyStoreConcurrencyException( 
                            version, 
                            expectedVersion, 
                            name); 
                    } 
                } 
            } 

            const string txt = @"INSERT INTO `ES_Events` (`Name`, `Version`, `Data`) VALUES(?name, ?version, ?data)"; 
            using (var cmd = new MySqlCommand(txt, conn, tx)) 
            { 
                cmd.Parameters.AddWithValue("?name", name);
```

## LƯU TRỮ DƯỚI DẠNG QUAN HỆ

```csharp
                cmd.Parameters.AddWithValue("?version", version+1); 
                cmd.Parameters.AddWithValue("?data", data); 
                cmd.ExecuteNonQuery(); 
            } 
            tx.Commit(); 
        } 
    } 
}
```

Việc đọc dữ liệu từ `IAppendOnlyStore` khá đơn giản, chỉ đòi hỏi một câu truy vấn cơ bản. Ví dụ, dưới đây là cách chúng ta lấy danh sách các bản ghi cho một Event Stream của Aggregate:

```csharp
public IEnumerable<DataWithVersion> ReadRecords( 
    string name, 
    int afterVersion, 
    int maxCount) 
{ 
    using (var conn = new MySqlConnection(_connectionString)) 
    { 
        conn.Open(); 
        const string sql = @"SELECT `Data`, `Version` FROM `ES_Events` WHERE `Name` = ?name AND `Version`>?version ORDER BY `Version` LIMIT 0,?take"; 
        using (var cmd = new MySqlCommand(sql, conn)) 
        { 
            cmd.Parameters.AddWithValue("?name", name); 
            cmd.Parameters.AddWithValue("?version", afterVersion); 
            cmd.Parameters.AddWithValue("?take", maxCount); 
            using (var reader = cmd.ExecuteReader()) 
            { 
                while (reader.Read()) 
                { 
                    var data = (byte[])reader["Data"]; 
                    var version = (int)reader["Version"]; 
                    yield return new DataWithVersion(version, data); 
                } 
            } 
        } 
    } 
}
```

Bạn sẽ tìm thấy mã nguồn đầy đủ cho Event Store dựa trên MySQL này cùng phần mã nguồn mẫu còn lại. Một bản triển khai tương tự cũng được cung cấp cho Microsoft SQL Server.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000635_a32bf8d4905e6a5d08ec052a79fffdacba255fa87ce5c827b081f03c8339c51f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000636_851aa746a06530da8c2af365e49bdab5cf8ff788f51d1d5a7e176360a614e155.png)

## Lưu Trữ Dưới Dạng BLOB

Tận dụng một máy chủ cơ sở dữ liệu (chẳng hạn như MySQL hay MS SQL Server) sẽ giúp bạn tiết kiệm rất nhiều công sức. Nó giúp giảm thiểu đáng kể nỗ lực trong việc xử lý quản lý đồng thời (concurrency management), phân mảnh tập tin (file fragmentation), lưu bộ nhớ đệm (caching), và tính nhất quán dữ liệu (data consistency). Vì vậy, hiển nhiên là nếu không sử dụng một sản phẩm cơ sở dữ liệu thì chúng ta sẽ phải tự mình giải quyết nhiều mối bận tâm trong số đó.

Tuy nhiên, nếu chúng ta quyết định dấn thân vào con đường gập ghềnh hơn để tự xây dựng các Event Store, chúng ta vẫn có được một số sự trợ giúp. Ví dụ, dịch vụ Windows Azure Blob storage và bộ lưu trữ tệp tin đơn giản (file system) đều có sẵn để sử dụng, và dự án mẫu cũng bao gồm các bản triển khai cho cả hai phương án này.

Hãy cùng xem xét một số chỉ dẫn thiết kế để xây dựng một Event Store không cần cơ sở dữ liệu, một vài trong số đó được tóm tắt qua Hình A.15:

1. Hệ thống lưu trữ tùy biến của chúng ta bao gồm một tập hợp chứa một hoặc nhiều tệp tin nhị phân lớn chỉ ghi thêm (append-only BLOB files - Binary Large Object) hoặc các thành phần tương đương. Thành phần thực hiện ghi vào bộ lưu trữ sẽ khóa độc quyền (exclusive lock) trong quá trình ghi thêm, nhưng vẫn cho phép các thao tác đọc đồng thời (concurrent reads).
2. Tùy thuộc vào chiến lược của bạn, bạn có thể chỉ sử dụng một kho lưu trữ BLOB duy nhất cho tất cả các loại và thực thể Aggregate thuộc một Bounded Context. Hoặc bạn có thể tạo một kho BLOB cho từng loại Aggregate, nơi lưu trữ toàn bộ các thực thể của loại đó. Hoặc bạn có thể chia tách các kho BLOB cho từng loại Aggregate theo từng thực thể riêng biệt, nơi mà Event Stream của một thực thể đơn lẻ sẽ được lưu trữ độc lập.
3. Khi thành phần ghi tiến hành ghi thêm, nó mở kho BLOB phù hợp, ghi dữ liệu vào đó, và duy trì một chỉ mục (index) dẫn vào kho lưu trữ.

Hình A.15 Lưu trữ BLOB dựa trên hệ thống tệp tin sử dụng chiến lược mỗi thực thể Aggregate là một tệp riêng, chứa một bản ghi cho mỗi Event

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000637_8e1fb061c337e86f5355ee23869cc27dc8095676e782fed0a1a7f2899debe977.png)

4. Bất kể chiến lược lưu trữ BLOB nào được sử dụng, toàn bộ các Event mới đều được ghi nối tiếp vào phần cuối. Mỗi bản ghi bao gồm các trường: tên (name), phiên bản (version), và dữ liệu nhị phân (binary data). Điều này tương tự như cách chúng ta lưu các bản ghi Event vào một cơ sở dữ liệu quan hệ. Tuy nhiên, với một kho lưu trữ BLOB, chúng ta phải thêm tiền tố độ dài byte vào trước các trường có độ dài thay đổi (variable-length fields), đồng thời gắn thêm một mã băm (hash code) hoặc kiểm tra dư thừa vòng (CRC - Cyclic Redundancy Check) để xác minh tính toàn vẹn của dữ liệu khi đọc các bản ghi.
5. Bộ lưu trữ chỉ ghi thêm dựa trên BLOB cho phép liệt kê toàn bộ các Event trên tất cả các Event Stream đơn giản bằng cách duyệt qua toàn bộ các tệp tin và nội dung của chúng. Để tăng tốc độ tìm kiếm trên đĩa (disk seeks) và việc đọc các Event cho một Stream cụ thể, chúng ta sẽ cần duy trì một chỉ mục riêng trong bộ nhớ (in-memory index) và/hoặc lưu bộ đệm các Event Stream trong bộ nhớ. Nếu sử dụng cơ chế lưu đệm trong bộ nhớ, mỗi lần ghi thêm sẽ đòi hỏi bộ nhớ đệm phải được làm mới (refreshed). Hơn nữa, việc chụp snapshot trạng thái Aggregate và chống phân mảnh tập tin (file defragmentation) cũng có thể giúp cải thiện hiệu năng.
6. Đương nhiên, chúng ta có thể tránh được nhiều vấn đề phân mảnh ổ đĩa của hệ thống tệp tin bằng cách cấp phát trước (preallocating) các vùng dung lượng lớn của tệp BLOB ngay khi từng Event Stream dạng tệp tin được tạo ra.

Thiết kế này được lấy cảm hứng từ mô hình Bitcask của Riak. Bạn có thể đọc thêm chi tiết và giải thích trong tài liệu kiến trúc Riak Bitcask: [http://downloads.basho.com/papers/bitcask-intro.pdf](http://downloads.basho.com/papers/bitcask-intro.pdf).

> 💡 **Giải thích thêm về "Riak Bitcask model":**
> Bitcask là một bộ máy lưu trữ (storage engine) log-structured key/value do Basho phát triển cho cơ sở dữ liệu Riak. Ý tưởng cốt lõi của nó là chỉ ghi dữ liệu tuần tự nối tiếp vào cuối tệp (append-only log files), đồng thời duy trì một bảng băm chỉ mục trong RAM (Keydir) trỏ trực tiếp đến vị trí offset của dữ liệu trên đĩa. Kiến trúc này mang lại thông lượng ghi cực cao, độ trễ đọc rất thấp (chỉ mất đúng một lần tìm kiếm trên đĩa), và khả năng phục hồi dữ liệu sau sự cố rất đơn giản.
> (Nguồn tham khảo: [https://riak.com/assets/bitcask-intro.pdf](https://riak.com/assets/bitcask-intro.pdf))

## Các Aggregate Tập Trung